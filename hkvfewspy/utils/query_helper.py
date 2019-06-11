def query(prefill_defaults=False, protocol='soap'):
    """
    Create a new query object.
    Returns a new :class:`DataQuery` instance appropriate for this endpoint.
    
    protocol : str
        choose between 'soap' or 'rest' (defaults to 'soap')

    Returns
    -------
    valid : bool
        Whether `query` is valid.
    """
    if prefill_defaults is True:
        # the following settings are not optional and therfore required.
        q_dflt = DataQuery(protocol)        
        q_dflt.convertDatum(False)        
        q_dflt.importFromExternalDataSource(False)
        q_dflt.omitMissing(False)
        q_dflt.onlyHeaders(False)
        q_dflt.onlyManualEdits(False)
        q_dflt.showEnsembleMemberIds(False)
        q_dflt.version("1.25")              
        q_dflt.documentFormat("PI_XML")
        q_dflt.showStatistics(False)
        q_dflt.showThresholds(False)
        q_dflt.useDisplayUnits(True)
        
        if protocol == 'soap':
            q_dflt.forecastSearchCount(0)
            q_dflt.clientTimeZone("Etc/GMT")
            q_dflt.showLocationAttributes(False)        
        
        return q_dflt
    else:
        return DataQuery(protocol)


class DataQuery(object):
    """
    Represent a query for data from a Delft-FEWS Pi client.
    This object provides a clear API to formulate a query for  timeseries data. For a getTimeSeries method.
    These objects provide a dictionary-like interface.
    """

    def __init__(self, protocol):
        """Construct an empty :class:`DataQuery`."""
        self.query = {}
        self.protocol = protocol

    def clientTimeZone(self, value="Etc/GMT"):
        """
        Set timezone how the timeseries should returns.
        Defaults to GMT.
        Parameters
        ----------
        value = str
            one of pytz supported timezones
        """
        if self.protocol == 'soap':
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
        if self.protocol == 'rest':
          self.query.update({"endCreationTime": value.isoformat(sep='T', timespec='auto')+'Z'})
        elif self.protocol == 'soap':
          self.query.update({"endCreationTime": value})

    def endForecastTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of end forecast time
        """        
        if self.protocol == 'rest':
          self.query.update({"endForecastTime": value.isoformat(sep='T', timespec='auto')+'Z'})
        elif self.protocol == 'soap':
          self.query.update({"endForecastTime": value})
        

    def endTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of end time
        """
        if self.protocol == 'rest':
          self.query.update({"endTime": value.isoformat(sep='T', timespec='auto')+'Z'})
        elif self.protocol == 'soap':
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
        if self.protocol == 'rest':
          self.query.update({"externalForecastTime": value.isoformat(sep='T', timespec='auto')+'Z'})
        elif self.protocol == 'soap':
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

    def version(self, value):
        """
        Parameters
        ----------
        value = str
            Pi version
        """
        if self.protocol == 'soap':
            self.query.update({"version": value})
        elif self.protocol == 'rest':
            self.query.update({"documentVersion": value})

    def documentFormat(self, value):
        """
        Parameters
        ----------
        value = str
            choose between PI_JSON or PI_XML
        """        
        if self.protocol == 'rest':
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
        if self.protocol == 'rest':
          self.query.update({"startCreationTime": value.isoformat(sep='T', timespec='auto')+'Z'})
        elif self.protocol == 'soap':
          self.query.update({"startCreationTime": value})         
        

    def startForecastTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of start forecast time
        """        
        if self.protocol == 'rest':
          self.query.update({"startForecastTime": value.isoformat(sep='T', timespec='auto')+'Z'})
        elif self.protocol == 'soap':
          self.query.update({"startForecastTime": value})           

    def startTime(self, value):
        """
        Parameters
        ----------
        value = datetime
            datetime of start time
        """
        if self.protocol == 'rest':
          self.query.update({"startTime": value.isoformat(sep='T', timespec='auto')+'Z'})
        elif self.protocol == 'soap':
          self.query.update({"startTime": value})          

    def useDisplayUnits(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"useDisplayUnits": value})
        
    def useMilliseconds(self, value):
        """
        Parameters
        ----------
        value = boolean
            true or false
        """
        self.query.update({"useMilliseconds": value})        

