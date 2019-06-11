import json
import requests
import types
import pandas as pd

from types import SimpleNamespace
from shapely.geometry import Point

class PiRest(object):
    """create Pi object that can interact with REST fewspi service
    """

    def __init__(self):
        """
        """
        self.url = 'https://db.dmhoutribdijk.nl/FewsWebServices/rest/fewspiservice/v1/'
        self.documentVersion = '1.25'
        self.documentFormat = 'PI_JSON'
        self.showAttributes = True

    def setQueryParameters(self, prefill_defaults=True):
        return query(prefill_defaults)

    def getTimeZoneId(self):
        """
        get the servers TimeZoneId

        all the results of get*** functions are also written back in the class object without 'get'
        (eg result of Pi.getTimeZoneId() is stored in Pi.TimeZoneId)
        """

        url = '{}timezoneid'.format(self.url)

        response = requests.get(url)
        setattr(self, 'TimeZoneId', response.text)
        return response.text

    def _addFilter(self, filter):
        """
        Add a filter to the collection
        """
        setattr(self.Filters, filter['id'].replace(".", "_"),
                {'id': filter['id'],
                 'name': filter['name']})

    def getFilters(self):
        """
        get the filters known at the Pi service, nested filters will be 'unnested'

        example : https://db.dmhoutribdijk.nl/FewsWebServices/rest/fewspiservice/v1/filters?documentFormat=PI_XML&documentVersion=1.25
                  https://db.dmhoutribdijk.nl/FewsWebServices/rest/fewspiservice/v1/filters?documentFormat=PI_XML&documentVersion=1.25
        """
        self.Filters = SimpleNamespace()

        url = '{}filters'.format(self.url)

        params = dict(
            documentVersion=self.documentVersion,
            documentFormat=self.documentFormat
        )

        response = requests.get(url, params=params)
        json_data = json.loads(response.text)

        for piFilter in json_data.get('filters'):
            keys = list(piFilter.keys())
            if 'child' in keys:
                for child in piFilter['child']:
                    keys = list(child.keys())
                    if 'child' in keys:
                        keys = list(child.keys())
                        for child in child['child']:
                            keys = list(child.keys())
                            if 'child' in keys:
                                for child in child['child']:
                                    self._addFilter(child)
                            self._addFilter(child)
                    self._addFilter(child)
            self._addFilter(piFilter)
        return pd.DataFrame(self.Filters.__dict__)

    def getLocations(self, filterId='', setFormat='df'):
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
        self.Locations = SimpleNamespace()
        self.Locations.dict = SimpleNamespace()

        url = '{}locations'.format(self.url)

        params = dict(
            filterId=filterId,
            documentVersion=self.documentVersion,
            documentFormat=self.documentFormat,
            showAttributes=self.showAttributes
        )

        response = requests.get(url, params=params)
        json_data = json.loads(response.text)
        locations = json_data.get('locations')

        for location in json_data.get('locations'):
            if location['locationId'][:1].isdigit():
                locId = "L{0}".format(
                    location['locationId']).replace(".", "_")
            else:
                locId = location['locationId'].replace(".", "_")

            # set attributes of object with location items
            setattr(self.Locations.dict, locId,
                    {'locationId': location['locationId'],
                     'shortName': location['shortName'],
                     'lat': location['lat'],
                     'lon': location['lon'],
                     'x': location['x'],
                     'y': location['y']
                     })

        # CREATE dataframe of location rows dictionary
        df = pd.DataFrame(vars(self.Locations.dict)).T
        df = df.loc[df.index != "geoDatum"]
        df[['lon', 'lat']] = df[['lon', 'lat']].apply(
            pd.to_numeric, errors='coerce')

        try:
            import geopandas as gpd
            # CONVERT to geodataframe using latlon for geometry
            geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
            df = df.drop(['lon', 'lat'], axis=1)
            crs = {'init': 'epsg:4326'}
            gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
            setattr(self.Locations, 'asGeoDataFrame', gdf)
            setattr(self.Locations, 'asGeoJSON', gdf.to_json())
        except:
            pass

        setattr(self.Locations, 'asDataFrame',
                pd.DataFrame(self.Locations.dict.__dict__))

        if setFormat == 'geojson':
            try:
                return self.Locations.asGeoJSON
            except:
                print('geopandas was not installed, return as DataFrame')
                return self.Locations.asDataFrame

        if setFormat == 'gdf':
            try:
                return self.Locations.asGeoDataFrame
            except:
                print('geopandas was not installed, return as DataFrame')
                return self.Locations.asDataFrame

        if setFormat == 'df':
            return self.Locations.asDataFrame

        if setFormat == 'dict':
            return self.Locations.dict

    def getParameters(self, filterId=''):
        """
        get the parameters known at the Pi service given a certain filterId

        Parameters
        ----------
        filterId: st'
            provide a filterId (if not known, try Pi.getFilters() first)
        """
        self.Parameters = SimpleNamespace()

        url = '{}parameters'.format(self.url)

        params = dict(
            filterId=filterId,
            documentVersion=self.documentVersion,
            documentFormat=self.documentFormat
        )

        response = requests.get(url, params=params)
        json_data = json.loads(response.text)

        for piParameter in json_data.get('timeSeriesParameters'):
            setattr(self.Parameters, piParameter['id'].replace(".", "_"),
                    {'id': piParameter['id'],
                     'name': piParameter['name'],
                     'parameterType': piParameter['parameterType'],
                     'unit': piParameter['unit'],
                     'displayUnit': piParameter['displayUnit'],
                     'usesDatum': piParameter['usesDatum']})

        return pd.DataFrame.from_dict(self.Parameters.__dict__)

    def getTimeSeries(self, queryParameters, header='longform', setFormat='df', print_response=False):
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
        """
        self.TimeSeries = SimpleNamespace()

        url = '{}timeseries'.format(self.url)

        response = requests.get(url, params=queryParameters.query)
        json_data = json.loads(response.text)
        for piTimeserie in json_data.get('timeSeries'):
            print(piTimeserie)

        return pd.DataFrame.from_dict(self.TimeSeries.__dict__)


def query(prefill_defaults=False):
    """
    Create a new query object.
    Returns a new :class:`DataQuery` instance appropriate for this endpoint.

    Returns
    -------
    valid : bool
        Whether `query` is valid.
    """
    if prefill_defaults is True:
        # the following settings are not optional and therfore required.
        q_dflt = DataQuery()
        q_dflt.convertDatum(False)
        q_dflt.showEnsembleMemberIds(False)
        q_dflt.useDisplayUnits(False)
        q_dflt.showThresholds(True)
        q_dflt.omitMissing(True)
        q_dflt.onlyHeaders(False)
        q_dflt.showStatistics(False)
        q_dflt.documentVersion("1.25")
        q_dflt.documentFormat("PI_JSON")
        return q_dflt
    else:
        return DataQuery()


class DataQuery(object):
    """
    Represent a query for data from a Delft-FEWS Pi client.
    This object provides a clear API to formulate a query for  timeseries data. For a getTimeSeries method.
    These objects provide a dictionary-like interface.
    """

    def __init__(self):
        """Construct an empty :class:`DataQuery`."""
        self.query = {}

    def clientTimeZone(self, value="Etc/GMT"):
        """
        Set timezone how the timeseries should returns.
        Defaults to GMT.
        Parameters
        ----------
        value = str
            one of pytz supported timezones
        """
        self.query.update({"clientTimeZone": value})

    def convertDatum(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"convertDatum": value})

    def endCreationTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of end creation time
        """
        self.query.update({"endCreationTime": value})

    def endForecastTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of end forecast time
        """
        self.query.update({"endForecastTime": value})

    def endTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of end time
        """
        self.query.update({"endTime": value})

    def ensembleId(self, value):
        """
        Parameters
        ----------
        value = str
            id of ensemble
        """
        self.query.update({"ensembleId": value})

    def externalForecastTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of external forecast
        """
        self.query.update({"externalForecastTime": value})

    def filterId(self, value):
        """
        Parameters
        ----------
        value = str
            name of filter id
        """
        self.query.update({"filterId": value})

    def forecastSearchCount(self, value=0):
        """
        Parameters
        ----------
        value = int
            forecast search count (default = 0)
        """
        self.query.update({"forecastSearchCount": value})

    def importFromExternalDataSource(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"importFromExternalDataSource": value})

    def locationIds(self, value):
        """
        Parameters
        ----------
        value = list
            list of location ids
        """
        self.query.update({"locationIds": value})

    def moduleInstanceIds(self, value):
        """
        Parameters
        ----------
        value = list
            list of module instance ids
        """
        self.query.update({"moduleInstanceIds": value})

    def omitMissing(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"omitMissing": value})

    def onlyForecasts(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"onlyForecasts": value})

    def onlyHeaders(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"onlyHeaders": value})

    def onlyManualEdits(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"onlyManualEdits": value})

    def parameterIds(self, value):
        """
        Parameters
        ----------
        value = list
            list of parameter ids
        """
        self.query.update({"parameterIds": value})

    def documentVersion(self, value):
        """
        Parameters
        ----------
        value = str
            Pi version
        """
        self.query.update({"documentVersion": value})

    def documentFormat(self, value):
        """
        Parameters
        ----------
        value = str
            Document format (PI_XML or PI_JSON)
        """
        self.query.update({"documentFormat": value})

    def qualifierIds(self, value):
        """
        Parameters
        ----------
        value = list
            list of qualifier ids
        """
        self.query.update({"qualifierIds": value})

    def showStatistics(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"showStatistics": value})

    def showEnsembleMemberIds(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"showEnsembleMemberIds": value})

    def showLocationAttributes(self, value):
        """
        
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"showLocationAttributes": value})

    def showThresholds(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"showThresholds": value})

    def startCreationTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            list of location ids
        """
        self.query.update({"startCreationTime": value})

    def startForecastTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of start forecast time
        """
        self.query.update({"startForecastTime": value})

    def startTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of start time
        """
        self.query.update({"startTime": value})

    def useDisplayUnits(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"useDisplayUnits": value})


if __name__ == "__main__":

    pi = PiRest()

#    timeZoneId = pi.getTimeZoneId()

    filters = pi.getFilters()
    print(filters)

    locations = pi.getLocations(filterId='f_ruw_gevalideerd.ADV')
    print(locations)

    parameters = pi.getParameters(filterId='f_ruw_gevalideerd.ADV')
    print(parameters)

    query_parameters = pi.setQueryParameters(prefill_defaults=True)
    
    query_parameters.query['filterId'] = 'f_ruw_ongevalideerd.STA'
    query_parameters.query['locationIds'] = 'FL65'
    query_parameters.query['parameterIds'] = 'status.etro'
    qquery_parameters.query['startTime'] = '2019-06-05 11:00'
    qquery_parameters.query['endTime'] = '2019-06-05 13:00'

    timeseries = pi.getTimeSeries(query_parameters)
