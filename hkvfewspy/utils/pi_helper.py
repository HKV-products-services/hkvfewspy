from .simplenamespace import *

def pi_series(prefill_defaults=False):
    """
    Create a new query object.
    Returns a new :class:`DataQuery` instance appropriate for this endpoint.
    
    Returns
    -------
    valid : bool
        Whether `query` is valid.
    """
    if prefill_defaults == True:
        s_dflt = PiTimeSeries()
        s_dflt.root.timeZone('gmt')
        s_dflt.root.version('1.22') 
        return s_dflt
    else:
        return PiTimeSeries()

    
class InnerClassDescriptor(object):
    def __init__(self, cls):
        self.cls = cls
    def __get__(self, instance, outerclass):
        class Wrapper(self.cls):
            _outer = instance
        Wrapper.__name__ = self.cls.__name__
        return Wrapper
    
class PiTimeSeries(object):
    """
    Represent a query for data from a Delft-FEWS pi client.
    This object provides a clear API to formulate a query for  timeseries data. For a getTimeSeries method.
    These objects provide a dictionary-like interface.
    """

    def __init__(self):
        """Construct an empty :class:`DataQuery`."""
        # set new empty attribute in object for task
        self._pi_json = {}
        self.header = self._Header()
        self.root = self._Root()  
        self.events = self._Events().events
        
#         self.setattr('series',series = dict()
#         self.series.setattr(self, 'header', {})
#         self.series.setattr(self, 'properties', {})        
#         self.series.setattr(self, 'event', {})
#         self.series.setattr(self, 'domainAxisValues', {})
       
    @InnerClassDescriptor
    class _Root(object): 
        def _update_root(self, key, value):
            try:
                self._outer._pi_json.update(
                    {key: value}
                )
            except KeyError as e:
                print(e)

        def timeZone(self, value='Etc/GMT'):
            """
            The timeZone (in decimal hours shift from GMT) e.g. -1.0 or 3.5. If not present the default timezone configured in the general adapter or import module is used. Always written when exported from FEWS.
            
            Or
            
            Id of a time zone that is observing daylight saving time
            
            Possible IDs:
            AST - Alaska Standard Time, winter:GMT-9 summer:GMT-8
            PST - Pacific Standard Time, winter:GMT-8 summer:GMT-7
            MST - Mountain Standard Time, winter and summer:GMT-7
            CST - Central Standard Time, winter:GMT-6 summer:GMT-5
            IET - Eastern Standard Time, winter:GMT-5 summer:GMT-4
            CNT - Newfoundland Standard Time, winter:GMT-3:30 summer:GMT-2:30
            AGT - Argentine Time, winter:GMT-3 summer:GMT-2
            BET - Brasilia Time, winter:GMT-3 summer:GMT-2
            WET - Western European Time, winter:GMT+0 summer:GMT+1
            CET - Central European Time, winter:GMT+1 summer:GMT+2
            MET - Middle Europe Time, winter:GMT+1 summer:GMT+2
            EET - Eastern European Time, winter:GMT+2 summer:GMT+3
            AZT - Azerbaijan Time, winter:GMT+4 summer:GMT+5
            NET - Armenia Time, winter:GMT+4 summer:GMT+5
            AET - Australia Eastern Time (New South Wales), winter:GMT+10 summer:GMT+11
            AWT - Since 2013.01. Australia Western Time, winter:GMT+8 summer:GMT+9
            NST - New Zealand Standard Time, winter:GMT+12 summer:GMT+13
            
            Parameters
            ----------
            value = [float, str]
                if float, is decimal hours shift from GMT, e.g. -1.0 or 3.5
                if str, is the ID of a timezone observing DST.
            """
            self._update_root('timeZone', value)
        
        def version(self, value='1.22'):
            """
            The version of the published interface schemas
            
            Parameters
            ----------
            value = str
                PI schema version as string (defaults to '1.22')
            """
            self._update_root('version', value)
            
        def geoDatum(self, value='WGS 1984'):
            """
            The geographical datum for the location data. LOCAL indicates a local grid.
            
            Parameters
            ----------
            value = str
                choose from, 'LOCAL', 'WGS 1984, 'Ordnance Survey Great Britain 1936', 'TWD 1967', 'Gauss Krueger Meridian2',
                'Gauss Krueger Meridian3', 'Gauss Krueger Austria M34', 'Gauss Krueger Austria M31', 'Rijks Driehoekstelsel',
                'JRC', 'DWD', 'KNMI Radar', 'CH1903', 'PAK1', 'PAK2', 'SVY21'
            """
            self._update_root('geoDatum', value)            
                      
    
    @InnerClassDescriptor
    class _Header(object): 
            
        def _update_header(self, key, value):
            try:
                self._outer._pi_json['timeSeries'][0]['header'].update(
                    {key: value}
                )
            except KeyError as e:
                if e.args[0] == 'header':
                    self._outer._pi_json['timeSeries'][0]['header'] = {}
                    self._outer._pi_json['timeSeries'][0]['header'].update(
                        {key: value}
                    )    
                if e.args[0] == 'timeSeries':
                    self._outer._pi_json['timeSeries']= []
                    self._outer._pi_json['timeSeries'].append({})
                    self._outer._pi_json['timeSeries'][0]['header'] = {}
                    self._outer._pi_json['timeSeries'][0]['header'].update(
                        {key: value}
                    )
            
        def comment(self, value='commenting'):
            """
            use this field as a notebook to add comments, suggestions description of data entered etc.
            
            Parameters
            ----------
            value = str
                comment in string format
            """

            self._update_header('comment', value)        

        def timeSeriesType(self, value='instantaneous'):
            """
            Type of data, either accumulative or instantaneous. For accumulative data the time/date of the event is the moment at which the data was gathered.
            
            ----------
            value = str
                choose from 'accumulative', 'instantaneous' or 'mean' (defaults to 'instantaneous')
            """        
            self._update_header({'type': value})

        def locationId(self, value):
            """
            Location ID, defined by the model
            
            Parameters
            ----------
            value = str
                string with location ID
            """  
            self._update_header('locationId',value)        

        def parameterId(self, value):
            """
            Content of the data (Discharge, Precipitation, VPD); defined by the model
            
            Parameters
            ----------
            value = str
                string with parameter ID
            """  
            self._update_header('parameterId',value)

        def qualifierId(self, value):
            """
            Id that references an qualifier listed in the regionConfigFiles/Qualifiers.xsd
            
            Parameters
            ----------
            value = [str, list]
                string or list of strings with qualifiers
            """        
            self._update_header('qualifierId', value)

        def ensembleId(self, value):
            """
            Optional field for running ensembles. Ensemble id's in a time series set will override ensemble id's defined in the workflow.
            
            Parameters
            ----------
            value = str
                id of ensemble
            """        
            self._update_header('ensembleId', value)  

        def timeStep(self, unit, divider=1, multiplier=1):
            """
            The time unit element has three attributes, unit and divider and multiplier. the unit is second, minute, hour, week, month year. The divider attribute is optional (default = 1).
            
            Parameters
            ----------
            unit = str
                choose from 'second', 'minute', 'hour', 'day', 'week', 'month', 'year', 'nonequidistant'
            divider = int
                optional and defaults to 1
            multiplier = int
                optional and defaults to 1 
            """        
            self._update_header('timeStep', {'unit': unit, 'divider':divider, 'multiplier':multiplier}) 

        def startDate(self, date, time):
            """
            Start date and time for this period.
            
            Parameters
            ----------
            date = str
                date in format of '%Y-%m-%d'
            time = str
                time in format of '%H:%M:%S'
            """        
            self._update_header('startDate', {'date': date, 'time':time})

        def endDate(self, date, time):
            """
            End date and time for this period.
            
            Parameters
            ----------
            date = str
                date in format of '%Y-%m-%d'
            time = str
                time in format of '%H:%M:%S'
            """        
            self._update_header('endDate', {'date': date, 'time':time})

        def forecastDate(self, date, time):
            """
            Since version 1.5 date/time of the forecast. By default the forecastDate equals the start time
            
            Parameters
            ----------
            date = str
                date in format of '%Y-%m-%d'
            time = str
                time in format of '%H:%M:%S'
            """         
            self._update_header('forecastDate', {'date': date, 'time':time}) 

        def approvedDate(self, date, time):
            """
            Since version 1.20. Returns the time that simulated forecast was made current. In case of no longer current then the original approved time is returned.
            
            Parameters
            ----------
            date = str
                date in format of '%Y-%m-%d'
            time = str
                time in format of '%H:%M:%S'
            """        
            self._update_header('approvedDate', {'date': date, 'time':time})                

        def missVal(self, value):
            """
            Missing value definition for this TimeSeries. Defaults to NaN if left empty
            
            Parameters
            ----------
            value = float
                missing value for timeseries
            """        
            self._update_header('missVal', value)         

        def longName(self, value):
            """
            Optional long (descriptive) name
            
            Parameters
            ----------
            value = str
                descriptive name
            """        
            self._update_header('longName', value)                 

        def stationName(self, value):
            """
            Station name
            
            Parameters
            ----------
            value = str
                name of station
            """        
            self._update_header('stationName', value)                 

        def lat(self, value):
            """
            Latitude of station
            
            Parameters
            ----------
            value = float
                latitude of station
            """        
            self._update_header('lat', value)

        def lon(self, value):
            """
            Longitude of station
            
            Parameters
            ----------
            value = float
                longitude of station
            """        
            self._update_header('lon', value)

        def x(self, value):
            """
            X coordinate of station
            
            Parameters
            ----------
            value = float
                x coordinate of station
            """      
            self._update_header('x', value)

        def y(self, value):
            """
            Y coordinate of station
            
            Parameters
            ----------
            value = float
                y coordinate of station
            """        
            self._update_header('y', value)

        def z(self, value):
            """
            Z coordinate of station. From version 1.16 this optional element is only written when available. In 1.15 and earlier z=0.0 is used when z is not defined
            
            Parameters
            ----------
            value = float
                z coordinate of station
            """        
            self._update_header('z', value)

        def units(self, value):
            """
            Optional string that identifies the units used
            
            Parameters
            ----------
            value = str
                string containing the units of the timeseries
            """        
            self._update_header('units', value)

        def sourceOrganisation(self, value):
            """
            Name of source organisation
            
            Parameters
            ----------
            value = str
                optional name of source organisation
            """        
            self._update_header('sourceOrganisation', value)

        def sourceSystem(self, value):
            """
            Name of source system
            
            Parameters
            ----------
            value = str
                optional name of source system
            """         
            self._update_header('sourceSystem', value)

        def fileDescription(self, value):
            """
            Description of (the content of) this file
            
            Parameters
            ----------
            value = str
                optional file content description
            """        
            self._update_header('fileDescription', value)        

        def creationDate(self, value):
            """
            Optional element that maybe used by third parties. The element is not used by FEWS. It is neither written nor read.
            
            Parameters
            ----------
            value = str
                date in format of '%Y-%m-%d'
            """        
            self._update_header('creationDate', value)

        def creationTime(self, value):
            """
            Optional element that maybe used by third parties. The element is not used by FEWS. It is neither written nor read.
            
            Parameters
            ----------
            value = str
                time in format of '%H:%M:%S'
            """        
            self._update_header('creationTime', value)

        def region(self, value):
            """
            Code/description of the region. Needed if the id's can be the same in different regions.
            
            Parameters
            ----------
            value = str
                region id
            """        
            self._update_header('region', value)

        def thresholds(self, threshold_id, name, label):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """        
            self._update_header('thresholds', {'id': threshold_id, 'name':name, 'label': label})    

    @InnerClassDescriptor
    class _Events(object): 
            
        def _update_events(self, value):
            try:
                self._outer._pi_json['timeSeries'][0]['events'] = value
            except KeyError as e:
                if e.args[0] == 'events':
                    self._outer._pi_json['timeSeries'][0]['events'] = value    
                if e.args[0] == 'timeSeries':
                    self._outer._pi_json['timeSeries']= []
                    self._outer._pi_json['timeSeries'].append({})
                    self._outer._pi_json['timeSeries'][0]['events'] = value
            
        def events(self, value):
            """
            An Pandas DataFrame or Pandas Series with an unlimited number of events with a constant timeStep. Each TimeSeries should contain at least one element (records). The datetime and value attributes are required, multiple optional attributes are optional.
            
            Parameters
            ----------
            value = [pandas.Series, pandas.DataFrame]
                series or dataframe containing values.
            
            Expected format
            `pandas.Series`
            In case of a Pandas Series, the index is expected to consist out of datetime elements and the data is expected to contain the values.

            `pandas.DataFrame`
            In case of a Pandas DataFrame, the index is expected to consist out of datetime elements and the column names are mapped as follow:
            Required:
            - index containing datetime objects

            Optional column names:
            - `value`, contains the data values [int, float]
            - `minValue`, contains the min data values [int, float]
            - `maxValue`, containts the max data values [int, float]
            - `flag`, contains a flag indicator [int]
            - `flagSource`, contains the source of the flag indicator [str] :: Since version 1.11, validation rule, default codes are MAN (manual), MOD (modifier), SN (soft min), HN (hard min), SX (soft max), HX (hard max), ROR (rate of rise), ROF (rate of fall), SR (same reading), TS (time shift), SVS (secondary validation series), SVF (secondary validation flags)
            - `comment`, containts a comment [str] :: Since version 1.3
            - `user`, contains name of user [str] :: Since version 1.10                
            """    
            
            # check ifindex consist of date objects
            if not value.index.is_all_dates:
                raise ValueError('index does not exist or not contains datetime objects')                  

            if not value.index.name:
                index_name = 'index'
            else:
                index_name = value.index.name

            value = value.reset_index()
            value.rename(columns={index_name: 'datetime'}, inplace=True) 

            # parse datetime objects to seperate date and time column
            dates, times = zip(*[(d.date(), d.time()) for d in value['datetime']])
            value = value.assign(date=dates, time=times)
            value.drop('datetime', axis=1, inplace=True)

            # only select column names that are accepted
            given_names = list(value.columns)
            accepted_names = ['date', 'time', 'value', 'minValue', 'maxValue', 'flag', 'flagSource', 'comment', 'user']
            taken_names = list(set(given_names) & set(accepted_names))

            # parse to row oriented json
            value_json = value[taken_names].to_json(orient='records', date_format='iso').replace('T00:00:00.000Z', '') 

            # parse to pi-json object
            self._update_events(value_json)
          

