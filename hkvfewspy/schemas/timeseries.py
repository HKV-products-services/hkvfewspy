import xml.etree.ElementTree as etree
import pandas as pd
import numpy as np
import os

# TODO: add to_pi_json() method. (Both PiTimeSeries and PiTimeSeriesCollection should be able to call this method)
# TODO: adapt to_pi_xml() and to_pi_json() from PiTimeSeries by Mattijn. Probably more robust write methods.

class PiBase:
    """
    Mix-in class for functionality that applies to both PiTimeSeries and PiTimeSeriesCollection.

    """

    def to_pi_json(self, fnam):
        #TODO: write to_pi_json function.
        raise NotImplementedError()

    def to_pi_xml(self, fnam):
        """
        Write PiTimeSeries object to PI-XML file.

        Parameters
        ----------
        fnam: path
            path to XML file to be written

        TODO: allow events (timeseries lines) to accept other fields besides 'date', 'time', 'value', 'flag'

        """
        assert fnam.endswith(".xml"), "Output file should have '.xml' extension!"

        # first line of XML file
        line0 = '<?xml version="1.0" encoding="UTF-8"?>\n'

        # some definitions for timeseries XML file
        NS = r"http://www.wldelft.nl/fews/PI"
        FS = r"http://www.wldelft.nl/fews/fs"
        XSI = r"http://www.w3.org/2001/XMLSchema-instance"
        schemaLocation = r"http://fews.wldelft.nl/schemas/version1.0/Pi-schemas/pi_timeseries.xsd"
        timeseriesline = '<TimeSeries xmlns="{NS}" xmlns:xsi="{XSI}" xsi:schemaLocation="{NS} {schema}" version="{version}" xmlns:fs="{FS}">\n'

        # line templates
        paramline = "<{tag}>{param}</{tag}>\n"

        # write file
        with open(fnam, "w") as f:
            f.write(line0)
            f.write(timeseriesline.format(NS=NS, FS=FS, XSI=XSI, schema=schemaLocation, version=self.version))
            tzline = "\t" + paramline.format(tag="timeZone", param=self.timezone)
            f.write(tzline)
            # how best to do this? Needs to be generic for single series vs collection of series
            N = 1 if isinstance(self, FewsTimeSeries) else self.timeseries.shape[0]

            for i in range(N):
                if isinstance(self, FewsTimeSeries):
                    ts = self
                elif isinstance(self, FewsTimeSeriesCollection):
                    ts = self.timeseries["events"].iloc[i]
                # start series
                start = "\t" + "<series>\n"
                f.write(start)
                # write header
                hlines = []
                hstart = 2*"\t" + "<header>\n"
                hlines.append(hstart)
                for htag, hval in ts.header.items():
                    if htag.endswith("Date"):
                        try:
                            hdate = hval.strftime("%Y-%m-%d")
                            htime = hval.strftime("%H:%M:%S")
                        except AttributeError:
                            ts._update_header_dates()
                            hdate, htime = ts.header[htag].split(" ")
                        hline = '<{tag} date="{date}" time="{time}"/>\n'.format(tag=htag,
                                                                                date=hdate,
                                                                                time=htime)
                    elif htag.endswith("timeStep"):
                        hline = '<{tag} unit="{unit}"/>\n'.format(tag=htag, unit=hval)
                    else:
                        hline = paramline.format(tag=htag, param=hval)
                    hlines.append(3*"\t" + hline)
                hlines.append(2*"\t" + "</header>\n")
                f.writelines(hlines)

                # write timeseries
                dates = ts.timeseries.reset_index()["index"].apply(lambda s: pd.datetime.strftime(s, "%Y-%m-%d"))
                times = ts.timeseries.reset_index()["index"].apply(lambda s: pd.datetime.strftime(s, "%H:%M:%S"))
                values = ts.timeseries["value"].astype(str)
                flags = ts.timeseries["flag"].astype(str)
                events = 2*"\t" + '<event date="' + dates.values + '" time="' + times.values + \
                         '" value="' + values.values + '" flag="' + flags.values + '"/>\n'
                f.writelines(events)
                # end series
                f.write("\t" + "</series>\n")
            # end Timeseries
            f.write("</TimeSeries>\n")


class FewsTimeSeriesCollection(PiBase):
    """
    Object for XML data. Read from file, add/remove series manually and write to new XML file.

    """

    def __init__(self, timeseries=None, timezone=None, version=1.19):
        """
        Initializes PiTimeSeries object.

        Parameters
        ----------
        data: pd.DataFrame, default None
            DataFrame containing specific columns (as created by from_pi_xml() method). If None,
            an empty DataFrame is created with the default column names.

        timezone: float, default 1.
            float indicating timezone (default 1.0 for Netherlands)

        version: float, default 1.19
            version of the XML file

        """
        if timeseries is None:
            columns = ['endDate', 'events', 'lat', 'locationId', 'lon', 'missVal',
                       'moduleInstanceId', 'parameterId', 'startDate', 'stationName',
                       'timeStep', 'type', 'units', 'x', 'y']
            self.timeseries = pd.DataFrame(columns=columns)
        else:
            self.timeseries = timeseries
        self.timezone = 1.0 if timezone is None else timezone
        # Etc/GMT* follows POSIX standard, including counter-intuitive sign change: see https://stackoverflow.com/q/51542167/2459096
        if self.timezone >= 0:
            self.timezone = "Etc/GMT-" + str(self.timezone)
        else:
            self.timezone = "Etc/GMT+" + str(self.timezone)
        self.version = version


    def add_series(self, dfseries, metadata):
        """
        Add series to PiTimeSeries object.

        Parameters
        ----------
        dfseries: pd.DataFrame
            Timeseries to add, must have DateTimeIndex and have columns with name "value" and "flag"

        metadata: dict
            dictionary containing header. Common entries values for include 'x', 'y', 'lat', lon',
            'missVal', 'stationName', 'type', 'units', 'moduleInstanceId', 'qualifierId', 'parameterId',
            'locationId'

        Notes
        -----
        It is unclear whether the entries in header are required or optional.
        Some possible values for header entries are shown below
        in case they need to be supplied:
        - 'missVal': np.nan
        - 'stationName': np.nan
        - 'units': 'm'
        - 'type': 'instantaneous'

        """

        #TODO: additional checks needed for input to ensure write works succesfully? Check keys of header if correct fields are present?
        assert isinstance(dfseries.index, pd.core.indexes.datetimes.DatetimeIndex), "DataFrame needs to have DateTimeIndex!"
        assert {"value", "flag"} <= set(dfseries.columns), "DataFrame requires columns named 'value' and 'flag'!"

        # Append to existing DF or add new row to empty DF
        try:
            new_index = self.timeseries.index[-1] + 1
        except IndexError:
            new_index = 0

        # add metadata info to header
        for k, v in metadata.items():
            self.timeseries.loc[new_index, k] = v

        # add timeseries as FewsTimeSeries object
        pi_timeseries = FewsTimeSeries(timeseries=dfseries, header=metadata, timezone=1.0)
        self.timeseries.loc[new_index, "events"] = pi_timeseries

    @classmethod
    def from_pi_xml(cls, fname):
        """
        Create a PiXML object from an existing XML file:

        Parameters
        ----------
        fname: path
            path to XML file

        Returns
        -------
        cls: PiXML object
            returns PiXML object.

        """
        tree = etree.parse(fname)
        root=tree.getroot()
        data=[]

        # default timezone, overwritten if found in file
        tz = 1.0

        for i in range(len(root)):
            if root[i].tag.endswith("timeZone"):
                tz = np.float(root[i].text.replace(",", ".")) # you never know with those Dutchies if they put decimal commas...
            if root[i].tag.endswith('series'):
                series={}
                header={}
                date=[]
                flag=[]
                time=[]
                value=[]
                for j in range(len(root[i])):
                    if root[i][j].tag.endswith('header'):
                        for k in range(len(root[i][j])):
                            # check if start and end date are read correctly!
                            prop = root[i][j][k].tag.split('}')[-1]
                            val = root[i][j][k].text
                            header[prop] = val
                    elif root[i][j].tag.endswith('event'):
                        date.append(root[i][j].attrib['date'])
                        flag.append(root[i][j].attrib['flag'])
                        time.append(root[i][j].attrib['time'])
                        value.append(root[i][j].attrib['value'])
                # combine events in a dataframe
                index = pd.to_datetime([d + ' ' + t for d, t in zip(date, time)])
                timeseries = pd.DataFrame({'flag': flag, 'value': value}, index=index, dtype=float)
                pi_timeseries = FewsTimeSeries(timeseries=timeseries, header=header, timezone=tz)
                series.update(header)
                series['events'] = pi_timeseries
                data.append(series)
        return cls(timeseries=pd.DataFrame(data), timezone=tz)


class FewsTimeSeries(PiBase):

    def __init__(self, timeseries=None, header=None, timezone=None, version=1.19):
        self.header = header
        self.timeseries = timeseries
        self.timezone = 1.0 if timezone is None else timezone
        # Etc/GMT* follows POSIX standard, including counter-intuitive sign change: see https://stackoverflow.com/q/51542167/2459096
        if self.timezone >= 0:
            self.timezone = "Etc/GMT-" + str(self.timezone)
        else:
            self.timezone = "Etc/GMT+" + str(self.timezone)
        self.version = version

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return np.all(self.timeseries == other.timeseries) and (self.timezone == other.timezone) and (self.version == other.version) and (self.header == other.header)
        return False

    @classmethod
    def from_pi_xml(cls, fname):
        """
        Initialize PiTimeSeries object from XML file. Assumes file contains only one timeseries.
        If not, stops after reading the first timeseries. Use PiTimeSeriesCollection for
        reading in multiple timeseries.

        Parameters
        ----------
        fname: str
            path of PI XML file to read.


        Returns
        -------
        PiTimeSeries: PiTimeSeries object
            instance of PiTimeSeries object

        """
        tree = etree.parse(fname)
        root=tree.getroot()

        # default timeZone, overwritten if found in file
        tz = 1.0
        scount = 0 # count series to quit parsing after first series

        for i in range(len(root)):
            if root[i].tag.endswith("timeZone"):
                tz = np.float(root[i].text.replace(",", ".")) # ensure decimal point is used (not comma)
            if root[i].tag.endswith('series'):
                if scount >= 1: # ugly but effective method to only parsing first series
                    break
                header={}
                date=[]
                flag=[]
                time=[]
                value=[]
                for j in range(len(root[i])):
                    if root[i][j].tag.endswith('header'):
                        for k in range(len(root[i][j])):
                            prop = root[i][j][k].tag.split('}')[-1]
                            val = root[i][j][k].text
                            header[prop] = val
                    elif root[i][j].tag.endswith('event'):
                        date.append(root[i][j].attrib['date'])
                        flag.append(root[i][j].attrib['flag'])
                        time.append(root[i][j].attrib['time'])
                        value.append(root[i][j].attrib['value'])
                # combine events in a dataframe
                index = pd.to_datetime([d + ' ' + t for d, t in zip(date, time)])
                timeseries = pd.DataFrame({'flag': flag, 'value': value}, index=index, dtype=float)
                scount +=1
        return cls(timeseries=timeseries, header=header, timezone=tz)


    def _update_header_dates(self):
        """
        If read fails to fill in startDate and endDate retrieve these from the timeseries
        and update header.

        """
        hupdate = {}
        for hcol in ["startDate", "endDate"]:
            ind = 0 if hcol.startswith("start") else -1 # start or end date
            hdate = self.timeseries.index[ind].strftime("%Y-%m-%d")
            htime = self.timeseries.index[ind].strftime("%H:%M:%S")
            hupdate[hcol] = hdate + ' ' + htime
        self.header.update(hupdate)


    def plot(self, **kwargs):
        """
        Pass plot command to DataFrame.
        """
        self.timeseries.plot(**kwargs)


if __name__ == "__main__":
    # load 1 series from an XML and write to file
    pi_ts1 = FewsTimeSeries.from_pi_xml(fname=r"../notebooks/test_2series.xml")
    pi_ts1.to_pi_xml("temp_1series.xml")

    # load all series from an XML and write to file
    ts_all = FewsTimeSeriesCollection.from_pi_xml(fname=r"../notebooks/test_2series.xml")
    # add series to collection loaded above
    ts_all.add_series(pi_ts1.timeseries, pi_ts1.header)
    # write to file
    ts_all.to_pi_xml("temp_3series.xml")

    # type of timeseries events in FewsTimeSeriesCollection should be FewsTimeSeries:
    print(type(ts_all.timeseries.events[0]))

    # test equality of FewsTimeSeries and the same series in FewsTimeSeriesCollection
    print(ts_all.timeseries.events[0] == pi_ts1)

    # plot timeseries
    import matplotlib.pyplot as plt
    pi_ts1.plot(y="value")
    plt.show()
