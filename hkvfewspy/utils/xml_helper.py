from .simplenamespace import *

def pi_series(prefill_defaults):
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
        s_dflt.convertDatum(False)
        s_dflt.forecastSearchCount(0)
        s_dflt.importFromExternalDataSource(False)
        s_dflt.omitMissing(False)
        s_dflt.onlyHeaders(False)
        s_dflt.showEnsembleMemberIds(False)
        s_dflt.showStatistics(False)
        s_dflt.showThresholds(False)
        s_dflt.useDisplayUnits(True)
        s_dflt.version('1.22') 
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
            Set timezone how the timeseries should returns.
            Defaults to GMT.
            Parameters
            ----------
            value = str
                one of pytz supported timezones
            """
            self._update_root('timeZone', value)
        
        def version(self, value='1.22'):
            """
            Set version of pi
            Parameters
            ----------
            value = str
                one of pytz supported timezones
            """
            self._update_root('version', value)       
    
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
            Set timezone how the timeseries should returns.
            Defaults to GMT.
            Parameters
            ----------
            value = str
                one of pytz supported timezones
            """

            self._update_header('comment', value)        

        def timeSeriesType(self, value):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """        
            self.series.header.update({'type': value})

        def locationId(self, value):
            """
            Parameters
            ----------
            value = str
                string with location ID
            """  
            setattr(self.series.header, 'locationId',value)        

        def parameterId(self, value):
            """
            Parameters
            ----------
            value = str
                string with parameter ID
            """  
            setattr(self.series.header, 'parameterId',value)

        def domainParameterId(self, value):
            """
            Parameters
            ----------
            value = str or list
                string or list of strings with domain parameter ID
            """        
            self.series.header.update({'domainParameterId': value})

        def qualifierId(self, value):
            """
            Parameters
            ----------
            value = str or list
                string or list of strings with qualifiers
            """        
            self.series.header.update({'qualifierId': value})

        def ensembleId(self, value):
            """
            Parameters
            ----------
            value = str
                id of ensemble
            """        
            self.series.header.update({'ensembleId': value})  

        def timeStep(self, unit, divider, multiplier):
            """
            Parameters
            ----------
            value = datetime
                datetime of external forecast
            """        
            self.series.header.update({'timeStep': {'unit': unit, 'divider':divider, 'multiplier':multiplier}}) 

        def startDate(self, date, time):
            """
            Parameters
            ----------
            value = str
                name of filter id
            """        
            self.series.header.update({'startDate': {'date': date, 'time':time}})

        def endDate(self, date, time):
            """
            Parameters
            ----------
            value = str
                name of filter id
            """        
            self.series.header.update({'endDate': {'date': date, 'time':time}})

        def forecastDate(self, date, time):
            """
            Parameters
            ----------
            value = str
                name of filter id
            """        
            self.series.header.update({'forecastDate': {'date': date, 'time':time}}) 

        def approvedDate(self, date, time):
            """
            Parameters
            ----------
            value = str
                name of filter id
            """        
            self.series.header.update({'approvedDate': {'date': date, 'time':time}})                

        def missVal(self, value):
            """
            Parameters
            ----------
            value = int
                forecast search count (default = 0)
            """        
            self.series.header.update({'missVal': value})         

        def longName(self, value):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """        
            self.series.header.update({'longName': value})                 

        def stationName(self, value):
            """
            Parameters
            ----------
            value = list
                list of location ids
            """        
            self.series.header.update({'stationName': value})                 

        def lat(self, value):
            """
            Parameters
            ----------
            value = list
                list of module instance ids
            """        
            self.series.header.update({'lat': value})

        def lon(self, value):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """        
            self.series.header.update({'lon': value})

        def x(self, value):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """      
            self.series.header.update({'x': value})

        def y(self, value):
            """
            Parameters
            ----------
            value = list
                list of parameter ids
            """        
            self.series.header.update({'y': value})

        def z(self, value):
            """
            Parameters
            ----------
            value = str
                pi version
            """        
            self.series.header.update({'z': value})

        def units(self, value):
            """
            Parameters
            ----------
            value = list
                list of qualifier ids
            """        
            self.series.header.update({'units': value})

        def sourceOrganisation(self, value):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """        
            self.series.header.update({'sourceOrganisation': value})

        def sourceSystem(self, value):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """        
            self.series.header.update({'sourceSystem': value})

        def fileDescription(self, value):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """        
            self.series.header.update({'fileDescription': value})        

        def creationDate(self, value):
            """
            Parameters
            ----------
            value = datetime
                list of location ids
            """        
            self.series.header.update({'creationDate': value})

        def creationTime(self, value):
            """
            Parameters
            ----------
            value = datetime
                datetime of start forecast time
            """        
            self.series.header.update({'creationTime': value})

        def region(self, value):
            """
            Parameters
            ----------
            value = datetime
                datetime of start time
            """        
            self.series.header.update({'region': value})

        def thresholds(self, value):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """        
            self.series.header.update({'thresholds': value})    

