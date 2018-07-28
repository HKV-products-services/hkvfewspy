def query(prefill_defaults):
    """
    Create a new query object.
    Returns a new :class:`DataQuery` instance appropriate for this endpoint.
    
    Returns
    -------
    valid : bool
        Whether `query` is valid.
    """
    if prefill_defaults == True:
        q_dflt = DataQuery()
        q_dflt.convertDatum(False)
        q_dflt.forecastSearchCount(0)
        q_dflt.importFromExternalDataSource(False)
        q_dflt.omitMissing(False)
        q_dflt.onlyHeaders(False)
        q_dflt.showEnsembleMemberIds(False)
        q_dflt.showStatistics(False)
        q_dflt.showThresholds(False)
        q_dflt.useDisplayUnits(True)
        q_dflt.version('1.22') 
        return q_dflt
    else:
        return DataQuery()

class DataQuery(object):
    """
    Represent a query for data from a Delft-FEWS pi client.
    This object provides a clear API to formulate a query for  timeseries data. For a getTimeSeries method.
    These objects provide a dictionary-like interface.
    """

    def __init__(self):
        """Construct an empty :class:`DataQuery`."""
        self.query = {}
        
    def clientTimeZone(self, value='Etc/GMT'):
        """
        Set timezone how the timeseries should returns.
        Defaults to GMT.
        Parameters
        ----------
        value = str
            one of pytz supported timezones
        """
        self.query.update({'clientTimeZone': value})

    def convertDatum(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """        
        self.query.update({'convertDatum': value})

    def endCreationTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of end creation time
        """        
        self.query.update({'endCreationTime': value})        
        
    def endForecastTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of end forecast time
        """        
        self.query.update({'endForecastTime': value})         
        
    def endTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of end time
        """        
        self.query.update({'endTime': value})
        
    def ensembleId(self, value):
        """
        Parameters
        ----------
        value = str
            id of ensemble
        """        
        self.query.update({'ensembleId': value})  
        
    def externalForecastTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of external forecast
        """        
        self.query.update({'externalForecastTime': value}) 
        
    def filterId(self, value):
        """
        Parameters
        ----------
        value = str
            name of filter id
        """        
        self.query.update({'filterId': value}) 
        
    def forecastSearchCount(self, value=0):
        """
        Parameters
        ----------
        value = int
            forecast search count (default = 0)
        """        
        self.query.update({'forecastSearchCount': value})         
        
    def importFromExternalDataSource(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """        
        self.query.update({'importFromExternalDataSource': value})                 

    def locationIds(self, value):
        """
        Parameters
        ----------
        value = list
            list of location ids
        """        
        self.query.update({'locationIds': value})                 

    def moduleInstanceIds(self, value):
        """
        Parameters
        ----------
        value = list
            list of module instance ids
        """        
        self.query.update({'moduleInstanceIds': value})
        
    def omitMissing(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """        
        self.query.update({'omitMissing': value})
        
    def onlyHeaders(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """      
        self.query.update({'onlyHeaders': value})
        
    def parameterIds(self, value):
        """
        Parameters
        ----------
        value = list
            list of parameter ids
        """        
        self.query.update({'parameterIds': value})
        
    def version(self, value):
        """
        Parameters
        ----------
        value = str
            pi version
        """        
        self.query.update({'version': value})
        
    def qualifierIds(self, value):
        """
        Parameters
        ----------
        value = list
            list of qualifier ids
        """        
        self.query.update({'qualifierIds': value})
        
    def showStatistics(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """        
        self.query.update({'showStatistics': value})
        
    def showEnsembleMemberIds(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """        
        self.query.update({'showEnsembleMemberIds': value})
        
    def showThresholds(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """        
        self.query.update({'showThresholds': value})        
        
    def startCreationTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            list of location ids
        """        
        self.query.update({'startCreationTime': value})
        
    def startForecastTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of start forecast time
        """        
        self.query.update({'startForecastTime': value})
        
    def startTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of start time
        """        
        self.query.update({'startTime': value})
        
    def useDisplayUnits(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """        
        self.query.update({'useDisplayUnits': value})    