import json
import requests
import types
import pandas as pd
from datetime import datetime, date

import gzip
import io
from ..utils.simplenamespace import *
from ..utils.query_helper import query
from ..utils.pi_helper import *
import collections


class PiRest(object):
    """create Pi object that can interact with REST fewspi service"""

    def __init__(self):
        """ """
        self.documentVersion = "1.25"
        self.documentFormat = "PI_JSON"
        self.showAttributes = True

    class utils(object):
        @staticmethod
        def addFilter(self, child):
            setattr(
                self.Filters,
                child["id"].replace(".", "_"),
                {
                    "id": child["id"],
                    "name": child.name.cdata,
                    "description": child.description.cdata,
                },
            )

        @staticmethod
        def event_client_datetime(event, tz_server, tz_client="Europe/Amsterdam"):
            """
            Get datetime object in client time of an XML Element named event with attributes date and time
            input:
            event     : XML Element named event [eg: obj.TimeSeries.series.event[0]]
            tz_server : datetime abbreviation of the server timezone [eg: 'Etc/GMT']
            tz_client : datetime abbreviation of the client timezone [eg: 'Europe/Amsterdam']

            return
            event_client_time : an datetime object of the event in client timezome

            """
            # convert XML element date string to integer list
            event_server_date = list(
                map(int, event["date"].split("-"))
            )  # -> [yyyy, MM, dd]
            event_server_time = list(
                map(int, event["time"].split(":"))
            )  # -> [HH, mm, ss]

            # define server time
            server_time = datetime(
                event_server_date[0],
                event_server_date[1],
                event_server_date[2],
                event_server_time[0],
                event_server_time[1],
                event_server_time[2],
                tzinfo=pytz.timezone(tz_server),
            )
            client_timezone = pytz.timezone(tz_client)

            # returns datetime in the new timezone
            event_client_time = server_time.astimezone(client_timezone)

            return event_client_time

        @staticmethod
        def gzip_str(string_):
            """
            write string to gzip compressed bytes object
            """
            out = io.BytesIO()

            with gzip.GzipFile(fileobj=out, mode="w") as fo:
                fo.write(string_.encode())

            bytes_obj = out.getvalue()
            return bytes_obj

        @staticmethod
        def gunzip_bytes_obj(bytes_obj):
            """
            read string from gzip compressed bytes object
            """
            in_ = io.BytesIO()
            in_.write(bytes_obj)
            in_.seek(0)
            with gzip.GzipFile(fileobj=in_, mode="rb") as fo:
                gunzipped_bytes_obj = fo.read()

            return gunzipped_bytes_obj.decode()

    def setUrl(self, url):
        self.url = url

    def setQueryParameters(self, prefill_defaults=True, protocol="soap"):
        return query(prefill_defaults, protocol)

    def getTimeZoneId(self):
        """
        get the servers TimeZoneId

        all the results of get*** functions are also written back in the class object without 'get'
        (eg result of Pi.getTimeZoneId() is stored in Pi.TimeZoneId)
        """

        url = "{}timezoneid".format(self.url)

        response = requests.get(url)
        setattr(self, "TimeZoneId", response.text)
        return response.text

    def _addFilter(self, filter):
        """
        Add a filter to the collection
        """
        setattr(
            self.Filters,
            filter["id"].replace(".", "_"),
            {"id": filter["id"], "name": filter["name"]},
        )

    def getFilters(self):
        """
        get the filters known at the Pi service, nested filters will be 'unnested'

        example : https://db.dmhoutribdijk.nl/FewsWebServices/rest/fewspiservice/v1/filters?documentFormat=PI_XML&documentVersion=1.25
                  https://db.dmhoutribdijk.nl/FewsWebServices/rest/fewspiservice/v1/filters?documentFormat=PI_XML&documentVersion=1.25
        """
        self.Filters = types.SimpleNamespace()

        url = "{}filters".format(self.url)

        params = dict(
            documentVersion=self.documentVersion, documentFormat=self.documentFormat
        )

        response = requests.get(url, params=params)
        json_data = json.loads(response.text)

        for piFilter in json_data.get("filters"):
            keys = list(piFilter.keys())
            if "child" in keys:
                for child in piFilter["child"]:
                    keys = list(child.keys())
                    if "child" in keys:
                        keys = list(child.keys())
                        for child in child["child"]:
                            keys = list(child.keys())
                            if "child" in keys:
                                for child in child["child"]:
                                    self._addFilter(child)
                            self._addFilter(child)
                    self._addFilter(child)
            self._addFilter(piFilter)
        return pd.DataFrame(self.Filters.__dict__)

    def runTask(
        self,
        startTime,
        endTime,
        workflowId,
        userId=None,
        coldStateId=None,
        scenarioId=None,
        piParametersXml=None,
        timeZero=None,
        clientId=None,
        piVersion="1.22",
        description=None,
    ):
        """
        run a workflow known at the Pi service

        Parameters
        ----------
        clientId: str
        workflowId: str
        startTime: datetime
        timeZero: str,
        endTime: datetime,
        coldStateId: str,
        scenarioId: str,
        coldstateId: str,
        piParametersXml: xml object
        userId: str
        description: str
        useColdState: boolean
        piVersion: str
            described the version of XML that is returned from the Pi service
            (defaults to 1.22 as current version only can read version 1.22)
        piXmlContent: xml object

        """

        # set new empty attribute in object for task
        self.Task = types.SimpleNamespace()

        url = "{}runtask".format(self.url)
        if type(startTime) == date:
            startTime = datetime.combine(startTime, datetime.min.time())
        if startTime is not None:
            try:
                startTime = startTime.isoformat(sep="T", timespec="auto") + "Z"
            except TypeError as e:
                print(f"stateTime is not date or datetime type: {e}")

        if type(endTime) == date:
            endTime = datetime.combine(endTime, datetime.min.time())
        if endTime is not None:
            try:
                endTime = endTime.isoformat(sep="T", timespec="auto") + "Z"
            except TypeError as e:
                print(f"endTime is not date or datetime type: {e}")

        if type(timeZero) == date:
            timeZero = datetime.combine(timeZero, datetime.min.time())
        if timeZero is not None:
            try:
                timeZero = timeZero.isoformat(sep="T", timespec="auto") + "Z"
            except TypeError as e:
                print(f"timeZero is not date or datetime type: {e}")

        params = dict(
            workflowId=workflowId,
            startTime=startTime,
            timeZero=timeZero,
            endTime=endTime,
            coldStateId=coldStateId,
            scenarioId=scenarioId,
            userId=userId,
            description=description,
        )

        headers = {"Content-type": "application/x-www-form-urlencoded"}
        data = "piModelParametersXmlContent={}".format(piParametersXml)
        # post task
        postRunTask_response = requests.post(
            url, data=data, params=params, headers=headers
        )
        if postRunTask_response.status_code == 403:
            from html.parser import HTMLParser

            class MyHTMLParser(HTMLParser):
                def handle_data(self, data):
                    if not "body {" in data:
                        if hasattr(self, "colldata"):
                            self.colldata.append(data)
                        else:
                            self.colldata = [data]

            parser = MyHTMLParser()
            parser.feed(postRunTask_response.text)
            print("\n".join(parser.colldata))
        elif postRunTask_response.status_code == 400:
            print(postRunTask_response.text)
        else:
            runTask_response = parse_raw(postRunTask_response.text)
            # runTask_json = parse_raw(response.text)
            setattr(self, "Task", {"id": runTask_response})

            return self.Task

    def getTaskRunStatus(self, taskId, maxWaitMillis=1000):
        """
        get the task run status known at the Pi service given a certain taskId

        Parameters
        ----------
        taskId: str
            provide a taskId
        maxWaitMillis: int
            maximum allowed waiting time

        all the results of get*** functions are also written back in the class object without 'get'
        (eg result of Pi.getTimeZoneId() is stored in Pi.TimeZoneId)
        """

        # set new empty attribute in object for task
        self.TaskRunStatus = types.SimpleNamespace()

        url = "{}taskrunstatus".format(self.url)

        params = dict(taskId=taskId, maxWaitMillis=maxWaitMillis)

        response = requests.get(url, params=params)
        getTaskRunStatus_response = response.text

        if getTaskRunStatus_response == "I":
            getTaskRunStatus_label = "Invalid"
        elif getTaskRunStatus_response == "P":
            getTaskRunStatus_label = "Pending"
        elif getTaskRunStatus_response == "T":
            getTaskRunStatus_label = "Terminated"
        elif getTaskRunStatus_response == "R":
            getTaskRunStatus_label = "Running"
        elif getTaskRunStatus_response == "F":
            getTaskRunStatus_label = "Failed"
        elif getTaskRunStatus_response == "C":
            getTaskRunStatus_label = "Completed fully successful"
        elif getTaskRunStatus_response == "D":
            getTaskRunStatus_label = "Completed partly successful"
        elif getTaskRunStatus_response == "A":
            getTaskRunStatus_label = "Approved"
        elif getTaskRunStatus_response == "B":
            getTaskRunStatus_label = "Approved partly successfull"
        else:
            getTaskRunStatus_label = "No status available: {}".format(
                getTaskRunStatus_response
            )

        setattr(
            self,
            "TaskRunStatus",
            {"status": getTaskRunStatus_label, "code": getTaskRunStatus_response},
        )

        return self.TaskRunStatus

    def getLocations(self, filterId="", setFormat="df"):
        """
        get the locations known at the Pi service given a certain filterId

        Parameters
        ----------
        filterId: str
            provide a filterId (if not known, try Pi.getFilters() first)
        setFormat: str
            choose the format to return, currently supports 'geojson', 'gdf' en 'dict'
            'geojson' returns GeoJSON formatted output
            'gdf' returns a GeoDataFrame
            'df' returns a DataFrame
            'dict' returns a dictionary of locations
        """

        # set new empty attribute in object for locations
        self.Locations = types.SimpleNamespace()
        self.Locations.dict = types.SimpleNamespace()

        url = "{}locations".format(self.url)

        params = dict(
            filterId=filterId,
            documentVersion=self.documentVersion,
            documentFormat=self.documentFormat,
            showAttributes=self.showAttributes,
        )

        response = requests.get(url, params=params)
        json_data = json.loads(response.text)
        locations = json_data.get("locations")

        for location in json_data.get("locations"):
            if location["locationId"][:1].isdigit():
                locId = "L{0}".format(location["locationId"]).replace(".", "_")
            else:
                locId = location["locationId"].replace(".", "_")

            # set attributes of object with location items
            setattr(
                self.Locations.dict,
                locId,
                {
                    "locationId": location["locationId"],
                    "shortName": location["shortName"],
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "x": location["x"],
                    "y": location["y"],
                },
            )

        # CREATE dataframe of location rows dictionary
        df = pd.DataFrame(vars(self.Locations.dict)).T
        df = df.loc[df.index != "geoDatum"]
        df[["lon", "lat"]] = df[["lon", "lat"]].apply(pd.to_numeric, errors="coerce")

        try:
            import geopandas as gpd
            from shapely.geometry import Point

            # CONVERT to geodataframe using latlon for geometry
            geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
            df = df.drop(["lon", "lat"], axis=1)
            crs = {"init": "epsg:4326"}
            gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
            setattr(self.Locations, "asGeoDataFrame", gdf)
            setattr(self.Locations, "asGeoJSON", gdf.to_json())
        except:
            pass

        setattr(
            self.Locations, "asDataFrame", pd.DataFrame(self.Locations.dict.__dict__)
        )

        if setFormat == "geojson":
            try:
                return self.Locations.asGeoJSON
            except:
                print("geopandas was not installed, return as DataFrame")
                return self.Locations.asDataFrame

        if setFormat == "gdf":
            try:
                return self.Locations.asGeoDataFrame
            except:
                print("geopandas was not installed, return as DataFrame")
                return self.Locations.asDataFrame

        if setFormat == "df":
            return self.Locations.asDataFrame

        if setFormat == "dict":
            return self.Locations.dict

    def getParameters(self, filterId=""):
        """
        get the parameters known at the Pi service given a certain filterId

        Parameters
        ----------
        filterId: st'
            provide a filterId (if not known, try Pi.getFilters() first)
        """
        self.Parameters = types.SimpleNamespace()

        url = "{}parameters".format(self.url)

        params = dict(
            filterId=filterId,
            documentVersion=self.documentVersion,
            documentFormat=self.documentFormat,
        )

        response = requests.get(url, params=params)
        json_data = json.loads(response.text)

        for piParameter in json_data.get("timeSeriesParameters"):
            setattr(
                self.Parameters,
                piParameter["id"].replace(".", "_"),
                {
                    "id": piParameter["id"],
                    "name": piParameter["name"],
                    "parameterType": piParameter["parameterType"],
                    "unit": piParameter["unit"],
                    "displayUnit": piParameter["displayUnit"],
                    "usesDatum": piParameter["usesDatum"],
                },
            )

        return pd.DataFrame.from_dict(self.Parameters.__dict__)

    def getWorkflows(self):
        """
        get the workflows known at the Pi service

        Parameters
        ----------
        piVersion: str
            described the version of XML that is returned from the Pi service
            (defaults to 1.22 as current version only can read version 1.22)

        all the results of get*** functions are also written back in the class object without 'get'
        (eg result of Pi.getTimeZoneId() is stored in Pi.TimeZoneId)
        """

        self.Workflows = types.SimpleNamespace()

        url = "{}workflows".format(self.url)

        params = dict(documentVersion=self.documentVersion)
        # print(url)
        # print(params)
        response = requests.get(url, params=params)
        getWorkflows_response = response.text

        getWorkflows_json = parse_raw(getWorkflows_response)

        # iterate over the workflows and set in Pi object
        for piWorkflow in getWorkflows_json.workflows.workflow:
            setattr(
                self.Workflows,
                piWorkflow["id"].replace(".", "_"),
                {
                    "id": piWorkflow["id"],
                    "name": piWorkflow.name.cdata,
                    "description": piWorkflow.description.cdata,
                },
            )
        return pd.DataFrame.from_dict(self.Workflows.__dict__)

    def getTimeSeries(
        self,
        queryParameters,
        header="longform",
        setFormat="df",
        print_response=False,
        tz="Etc/GMT",
    ):
        """
        get the timeseries known at the Pi service given dict of query parameters

        Parameters
        ----------
        queryParameters: dict
            rest request parameters, use function setQueryParameters to set the dictioary
        header : str
            how to parse the returned header object. Choose from:
            - 'longform', has one row per observation, with metadata recorded within the table as values.
            - 'multiindex', tries to parse the header into a single pandas.DataFrame where the header is contained as multi-index.
            - 'dict', parse the events of the response in a pandas.DataFrame and the header in a seperate dictionary
        setFormat: str
            choose the format to return, currently supports 'geojson', 'gdf' en 'dict'
            - 'json' returns JSON formatted output
            - 'df' returns a DataFrame
            - 'gzip' returns a Gzip compresed JSON string
        print_response: boolean
            if True, prints the xml return
        tz : str
            set locat client timezone
        """
        self.TimeSeries = types.SimpleNamespace()

        url = "{}timeseries".format(self.url)
        # check if input is a queryParameters is class and not dictionary
        if not isinstance(queryParameters, collections.Mapping):
            # if so try extract the query
            queryParameters = queryParameters.query

        response = requests.get(url, params=queryParameters)
        if print_response == True:
            print(response.text)

        df_timeseries = read_timeseries_response(
            response.text, tz_client=tz, header=header
        )

        setattr(self.TimeSeries, "asDataFrame", df_timeseries)
        setattr(
            self.TimeSeries,
            "asJSON",
            df_timeseries.reset_index().to_json(orient="records", date_format="iso"),
        )
        setattr(self.TimeSeries, "asGzip", self.utils.gzip_str(self.TimeSeries.asJSON))

        if setFormat == "json":
            return self.TimeSeries.asJSON
        elif setFormat == "df":
            return self.TimeSeries.asDataFrame
        elif setFormat == "gzip":
            return self.TimeSeries.asGzip

    def setPiTimeSeries(self, prefill_defaults=True):
        return set_pi_timeseries(prefill_defaults)

    def postTimeSeries(self, filterId, piTimeSeriesXmlContent, convertDatum=False):  #
        """
        put the timeseries into a Pi service given a pi timeseries object

        Parameters
        ----------
        filterId: str
            provide a filterId (if not known, try Pi.getFilters() first)
        piTimeSeriesXmlContent : str (xml-object)
            xml string of pi-timeseries object or timeseries object eg created with setPiTimeSeries,
            where the xml can be derived with .to.pi_xml()
        convertDatum: boolean
            Option to convert values from relative to location height to absolute values (True). If False values remain relative. (default is True)
        """
        url = "{}timeseries".format(self.url)
        params = {"filterId": filterId, "convertDatum": convertDatum}
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        data = "piTimeSeriesXmlContent={}".format(piTimeSeriesXmlContent)
        # post timeseries
        postTimeSeries_response = requests.post(
            url, data=data, params=params, headers=headers
        )

        doc = parse_raw(postTimeSeries_response.text)
        msg_list = []
        for idx in range(len(doc.Diag.line)):
            messg = doc.Diag.line[idx]["description"]
            messg = messg.replace("Import.Info: ", "")
            messg = messg.replace("Import.info: ", "")
            msg_list.append(messg)

        print("\n".join(msg_list))
