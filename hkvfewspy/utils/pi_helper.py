from .simplenamespace import *
from ..utils.untangle import parse_raw
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta
import pytz
import types
import copy
import ast
import json
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree
import logging
    
class InnerClassDescriptor(object):
    def __init__(self, cls):
        self.cls = cls
    def __get__(self, instance, outerclass):
        class Wrapper(self.cls):
            _outer = instance
        Wrapper.__name__ = self.cls.__name__
        return Wrapper
    
class SetPiTimeSeries(object):
    """
    Represent a query for data from a Delft-FEWS Pi client.
    This object provides a clear API to formulate a query for  timeseries data. For a getTimeSeries method.
    These objects provide a dictionary-like interface.
    """

    def __init__(self):
        """Construct an empty :class:`DataQuery`."""
        # set new empty attribute in object for task
        #python3.x: obj = types.SimpleNamespace()
        self.to = types.SimpleNamespace()
        self.write = types.SimpleNamespace()
        self.view = {}
        #self.to._pi_json = {}
        self.to._pi_xml = {}
        self.to.pi_json = self._pi_json
        self.to.pi_xml = self._pi_xml 
        self.write.header = self._Header()
        self.write.comment = self._Comment().comment
        self.write.properties = self._Properties()
        self.write.root = self._Root()  
        self.write.events = self._Events().events
        
#         self.setattr("series",series = dict()
#         self.series.setattr(self, "header", {})
#         self.series.setattr(self, "properties", {})        
#         self.series.setattr(self, "event", {})
#         self.series.setattr(self, "domainAxisValues", {})

    def _pi_json(self):
        """
        parse Pi timeseries to PI-JSON
        source is JSON-dict for headers and pandas.DataFrame as events
        """
        obj = copy.deepcopy(self.view)
        if 'timeSeries' in obj:
            obj_df = obj["timeSeries"][0]["events"]
            
            obj_df = obj_df.reset_index()

            # parse datetime objects to seperate date and time column
            dates, times = zip(*[(d.date(), d.time()) for d in obj_df["datetime"]])
            obj_df = obj_df.assign(date=dates, time=times)
            obj_df.drop("datetime", axis=1, inplace=True)
            
            obj_json = obj_df.to_json(orient="records", date_format="iso").replace("T00:00:00.000Z", "")
            obj_json = ast.literal_eval(obj_json)
            obj["timeSeries"][0]["events"] = obj_json
        
        obj = json.dumps(obj, indent=4, sort_keys=True)
        
        return obj
    
    def _pi_xml(self):
        """
        parse Pi timeseries to PI-XML
        source is JSON-dict for headers and pandas.DataFrame as events
        """
        # prepare objects to write to XML
        obj = copy.deepcopy(self.view)
        if 'timeSeries' in obj:
            if 'events' in obj['timeSeries'][0]: 
                e = obj['timeSeries'][0]['events']
                e = e.reset_index()

                # parse datetime objects to seperate date and time column
                dates, times = zip(*[(d.date(), d.time()) for d in e["datetime"]])
                e = e.assign(date=dates, time=times)
                e.drop("datetime", axis=1, inplace=True)            
            else:
                e = pd.DataFrame()
            if 'comment' in obj['timeSeries'][0]: 
                c = obj['timeSeries'][0]
            else:
                c = []    
            if 'header' in obj['timeSeries'][0]: 
                h = obj['timeSeries'][0]['header']
            else:
                h = []
            if 'comment' in obj['timeSeries'][0]: 
                c = obj['timeSeries'][0]['comment']
            if 'properties' in obj['timeSeries'][0]: 
                p = obj['timeSeries'][0]['properties']
            else:
                p = []
        
        # start writing XML block
        root = Element('TimeSeries')
        root.set('xmlns','http://www.wldelft.nl/fews/PI')
        root.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:schemaLocation','http://www.wldelft.nl/fews/PI http://fews.wldelft.nl/schemas/version1.0/pi-schemas/pi_timeseries.xsd')
        if 'version' in obj: root.set('version',obj['version'])

        if 'timeZone' in obj: SubElement(root, 'timeZone').text = obj['timeZone']
        if 'geoDatum' in obj: SubElement(root, 'geoDatum').text = obj['geoDatum']

        # COMMENT child
        if 'c' in locals():
            ch1 = SubElement(root, 'series')        
            if c: SubElement(ch1, 'comment').text = c

        # HEADER child
        if 'h' in locals():        
            sbch1 = SubElement(ch1, 'header')
            if 'type' in h: SubElement(sbch1, 'type').text = h['type']
            if 'moduleInstanceId' in h: SubElement(sbch1, 'moduleInstanceId').text = h['moduleInstanceId']    
            if 'locationId' in h: SubElement(sbch1, 'locationId').text = h['locationId']
            if 'parameterId' in h: SubElement(sbch1, 'parameterId').text = h['parameterId']
            if 'qualifierId' in h: SubElement(sbch1, 'qualifierId').text = h['qualifierId']
            if 'ensembleId' in h: SubElement(sbch1, 'ensembleId').text = h['ensembleId']    
            if 'timeStep' in h: 
                sbch1sb1 = SubElement(sbch1, 'timeStep')
                sbch1sb1.set('unit', h['timeStep']['unit'])
                if str(h['timeStep']['divider']) == str(1):
                    sbch1sb1.set('multiplier', str(h['timeStep']['multiplier']))
                else:
                    sbch1sb1.set('divider', str(h['timeStep']['divider']))
            if 'startDate' in h: 
                sbch1sb2 = SubElement(sbch1, 'startDate')
                sbch1sb2.set('date', h['startDate']['date'])
                sbch1sb2.set('time', h['startDate']['time'])
            if 'endDate' in h: 
                sbch1sb3 = SubElement(sbch1, 'endDate')
                sbch1sb3.set('date', h['endDate']['date'])
                sbch1sb3.set('time', h['endDate']['time'])
            if 'forecastDate' in h: 
                sbch1sb4 = SubElement(sbch1, 'forecastDate')
                sbch1sb4.set('date', h['forecastDate']['date'])
                sbch1sb4.set('time', h['forecastDate']['time']) 
            if 'approvedDate' in h: 
                sbch1sb5 = SubElement(sbch1, 'approvedDate')
                sbch1sb5.set('date', h['approvedDate']['date'])
                sbch1sb5.set('time', h['approvedDate']['time'])     
            if 'missVal' in h: SubElement(sbch1, 'missVal').text = str(h['missVal'])
            if 'longName' in h: SubElement(sbch1, 'longName').text = str(h['longName'])
            if 'stationName' in h: SubElement(sbch1, 'stationName').text = str(h['stationName'])
            if 'lat' in h: SubElement(sbch1, 'lat').text = str(h['lat'])
            if 'lon' in h: SubElement(sbch1, 'lon').text = str(h['lon'])
            if 'x' in h: SubElement(sbch1, 'x').text = str(h['x'])
            if 'y' in h: SubElement(sbch1, 'y').text = str(h['y'])
            if 'z' in h: SubElement(sbch1, 'z').text = str(h['z'])   
            if 'units' in h: SubElement(sbch1, 'units').text = str(h['units'])
            if 'sourceOrganisation' in h: SubElement(sbch1, 'sourceOrganisation').text = str(h['sourceOrganisation'])
            if 'sourceSystem' in h: SubElement(sbch1, 'sourceSystem').text = str(h['sourceSystem'])     
            if 'fileDescription' in h: SubElement(sbch1, 'fileDescription').text = str(h['fileDescription'])
            if 'creationDate' in h: SubElement(sbch1, 'creationDate').text = str(h['creationDate'])
            if 'creationTime' in h: SubElement(sbch1, 'creationTime').text = str(h['creationTime'])   
            if 'region' in h: SubElement(sbch1, 'region').text = str(h['region'])
            if 'thresholds' in h: 
                sbch1sb6 = SubElement(sbch1, 'thresholds')
                sbch1sb6.set('id', h['thresholds']['id'])
                sbch1sb6.set('name', h['thresholds']['name'])     
                sbch1sb6.set('label', h['thresholds']['label'])         

        # PROPERTIES child
        if 'p' in locals():          
            sbch2 = SubElement(ch1, 'properties')
            if 'description' in p: SubElement(sbch2, 'description').text = p['description']
            if 'string' in p: 
                sbch2sb1 = SubElement(sbch2, 'string')
                sbch2sb1.set('key', h['string']['key'])
                sbch2sb1.set('value', h['string']['value']) 
            if 'int' in p: 
                sbch2sb2 = SubElement(sbch2, 'int')
                sbch2sb2.set('key', h['int']['key'])
                sbch2sb2.set('value', h['int']['value'])
            if 'float' in p: 
                sbch2sb3 = SubElement(sbch2, 'float')
                sbch2sb3.set('key', h['float']['key'])
                sbch2sb3.set('value', h['float']['value'])
            if 'double' in p: 
                sbch2sb4 = SubElement(sbch2, 'double')
                sbch2sb4.set('key', h['double']['key'])
                sbch2sb4.set('value', h['double']['value'])
            if 'datetime' in p: 
                sbch2sb5 = SubElement(sbch2, 'datetime')
                sbch2sb5.set('key', h['datetime']['key'])
                sbch2sb5.set('date', h['datetime']['date'])
                sbch2sb5.set('time', h['datetime']['time'])    
            if 'bool' in p: 
                sbch2sb6 = SubElement(sbch2, 'bool')
                sbch2sb6.set('key', h['bool']['key'])
                sbch2sb6.set('value', h['bool']['value'])    

        # EVENTS children
        if 'e' in locals():         
            for row in e.iterrows():
                sbch3 = SubElement(ch1, 'event')
                if 'date' in row[1].index: 
                    sbch3.set('date', row[1].date.strftime(format='%Y-%m-%d'))
                else:
                    raise('date column is required')
                if 'time' in row[1].index:         
                    sbch3.set('time', row[1].time.strftime(format='%H:%M:%S.%f')[:-3])
                else:
                    raise('time column is required')        
                if 'value' in row[1].index: sbch3.set('value', str(row[1].value))
                if 'minValue' in row[1].index: sbch3.set('minValue', str(row[1].minValue))
                if 'maxValue' in row[1].index: sbch3.set('maxValue', str(row[1].maxValue))
                if 'flag' in row[1].index: sbch3.set('flag', str(row[1].flag))
                if 'flagSource' in row[1].index: sbch3.set('flagSource', str(row[1].flagSource))
                if 'comment' in row[1].index: sbch3.set('comment', str(row[1].comment))
                if 'user' in row[1].index: sbch3.set('user', str(row[1].user))
        
        obj = prettify(root)
        return obj
        

    @InnerClassDescriptor
    class _Root(object): 
        def _update_root(self, key, value):
            try:
                self._outer.view.update(
                    {key: value}
                )
            except KeyError as e:
                print(e)

        def timeZone(self, value="Etc/GMT"):
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
            self._update_root("timeZone", value)
        
        def version(self, value="1.22"):
            """
            The version of the published interface schemas
            
            Parameters
            ----------
            value = str
                PI schema version as string (defaults to "1.22")
            """
            self._update_root("version", value)
            
        def geoDatum(self, value="WGS 1984"):
            """
            The geographical datum for the location data. LOCAL indicates a local grid.
            
            Parameters
            ----------
            value = str
                choose from, "LOCAL", "WGS 1984, "Ordnance Survey Great Britain 1936", "TWD 1967", "Gauss Krueger Meridian2",
                "Gauss Krueger Meridian3", "Gauss Krueger Austria M34", "Gauss Krueger Austria M31", "Rijks Driehoekstelsel",
                "JRC", "DWD", "KNMI Radar", "CH1903", "PAK1", "PAK2", "SVY21"
            """
            self._update_root("geoDatum", value)            
                      
    @InnerClassDescriptor
    class _Comment(object): 
            
        def _update_comment(self, key, value):
            try:
                self._outer.view["timeSeries"][0].update(
                    {key: value}
                )
            except KeyError as e:   
                if e.args[0] == "timeSeries":
                    self._outer.view["timeSeries"]= []
                    self._outer.view["timeSeries"].append({})
                    self._outer.view["timeSeries"][0].update(
                        {key: value}
                    )
            
        def comment(self, value="commenting"):
            """
            use this field as a notebook to add comments, suggestions description of data entered etc.
            
            Parameters
            ----------
            value = str
                comment in string format
            """

            self._update_comment("comment", value)  
            
    @InnerClassDescriptor
    class _Properties(object): 
            
        def _update_properties(self, key, value):
            try:
                self._outer.view["timeSeries"][0]["properties"].update(
                    {key: value}
                )
            except KeyError as e:   
                if e.args[0] == "properties":
                    self._outer.view["timeSeries"][0]["properties"] = {}
                    self._outer.view["timeSeries"][0]["properties"].update(
                        {key: value}
                    )                  
                if e.args[0] == "timeSeries":
                    self._outer.view["timeSeries"]= []
                    self._outer.view["timeSeries"].append({})
                    self._outer.view["timeSeries"][0]['properties'] = {}
                    self._outer.view["timeSeries"][0]['properties'].update(
                        {key: value}
                    )
                    
                    
            
        def description(self, value):
            """
            Since 2014.01. Properties that are applicable to the events following
            use this field as description for the events that follow.
            
            Parameters
            ----------
            value = str
                description in string format
            """

            self._update_properties("description", value)    
            
        def string_type(self, description, key, value):
            """
            Since 2014.01. Properties that are applicable to the events following
            make use this field as description for the events that follow.
            
            Parameters
            ----------
            key = str
                key in string format            
            value = str
                value in string format
            """

            self._update_properties("string", {"key":key, "value":value})

        def int_type(self, description, key, value):
            """
            Since 2014.01. Properties that are applicable to the events following
            make use this field as description for the events that follow.
            
            Parameters
            ----------
            key = str
                key in string format            
            value = str
                value in string format
            """

            self._update_properties("int", {"key":key, "value":value})
            
        def float_type(self, description, key, value):
            """
            Since 2014.01. Properties that are applicable to the events following
            make use this field as description for the events that follow.
            
            Parameters
            ----------
            key = str
                key in string format            
            value = str
                value in string format
            """

            self._update_properties("float", {"key":key, "value":value})             
            
        def double_type(self, description, key, value):
            """
            Since 2014.01. Properties that are applicable to the events following
            make use this field as description for the events that follow.
            
            Parameters
            ----------
            key = str
                key in string format            
            value = str
                value in string format
            """

            self._update_properties("double", {"key":key, "value":value})    
            
        def datetime_type(self, description, key, date, time):
            """
            Since 2014.01. Properties that are applicable to the events following
            make use this field as description for the events that follow.
            
            Parameters
            ----------
            key = str
                key in string format            
            date = str
                date in %Y-%m-%d format
            time = str
                time in %H:%M:%S.%f format                
            """

            self._update_properties("datetime", {"key":key, "date":date, "time":time})
            
        def boolean_type(self, description, key, date, time):
            """
            Since 2014.01. Properties that are applicable to the events following
            make use this field as description for the events that follow.
            
            Parameters
            ----------
            key = str
                key in string format            
            value = str
                value in string format               
            """

            self._update_properties("bool", {"key":key, "value":value})            
                
    @InnerClassDescriptor
    class _Header(object): 
            
        def _update_header(self, key, value):
            try:
                self._outer.view["timeSeries"][0]["header"].update(
                    {key: value}
                )
            except KeyError as e:
                if e.args[0] == "header":
                    self._outer.view["timeSeries"][0]["header"] = {}
                    self._outer.view["timeSeries"][0]["header"].update(
                        {key: value}
                    )    
                if e.args[0] == "timeSeries":
                    self._outer.view["timeSeries"]= []
                    self._outer.view["timeSeries"].append({})
                    self._outer.view["timeSeries"][0]["header"] = {}
                    self._outer.view["timeSeries"][0]["header"].update(
                        {key: value}
                    )
    

        def timeSeriesType(self, value="instantaneous"):
            """
            Type of data, either accumulative or instantaneous. For accumulative data the time/date of the event is the moment at which the data was gathered.
            
            ----------
            value = str
                choose from "accumulative", "instantaneous" or "mean" (defaults to "instantaneous")
            """        
            self._update_header("type", value)

        def moduleInstanceId(self, value):
            """
            module instance ID, defined by the model
            
            Parameters
            ----------
            value = str
                string with module instance ID
            """  
            self._update_header("moduleInstanceId",value)    
            
        def locationId(self, value):
            """
            Location ID, defined by the model
            
            Parameters
            ----------
            value = str
                string with location ID
            """  
            self._update_header("locationId",value)        

        def parameterId(self, value):
            """
            Content of the data (Discharge, Precipitation, VPD); defined by the model
            
            Parameters
            ----------
            value = str
                string with parameter ID
            """  
            self._update_header("parameterId",value)

        def qualifierId(self, value):
            """
            Id that references an qualifier listed in the regionConfigFiles/Qualifiers.xsd
            
            Parameters
            ----------
            value = [str, list]
                string or list of strings with qualifiers
            """        
            self._update_header("qualifierId", value)

        def ensembleId(self, value):
            """
            Optional field for running ensembles. Ensemble id"s in a time series set will override ensemble id"s defined in the workflow.
            
            Parameters
            ----------
            value = str
                id of ensemble
            """        
            self._update_header("ensembleId", value)  

        def timeStep(self, unit, divider=1, multiplier=1):
            """
            The time unit element has three attributes, unit and divider and multiplier. the unit is second, minute, hour, week, month year. The divider attribute is optional (default = 1).
            
            Parameters
            ----------
            unit = str
                choose from "second", "minute", "hour", "day", "week", "month", "year", "nonequidistant"
            divider = int
                optional and defaults to 1
            multiplier = int
                optional and defaults to 1 
            """        
            self._update_header("timeStep", {"unit": unit, "divider":divider, "multiplier":multiplier}) 

        def startDate(self, date, time):
            """
            Start date and time for this period.
            
            Parameters
            ----------
            date = str
                date in format of "%Y-%m-%d"
            time = str
                time in format of "%H:%M:%S.%f"
            """        
            self._update_header("startDate", {"date": date, "time":time})

        def endDate(self, date, time):
            """
            End date and time for this period.
            
            Parameters
            ----------
            date = str
                date in format of "%Y-%m-%d"
            time = str
                time in format of "%H:%M:%S.%f"
            """        
            self._update_header("endDate", {"date": date, "time":time})

        def forecastDate(self, date, time):
            """
            Since version 1.5 date/time of the forecast. By default the forecastDate equals the start time
            
            Parameters
            ----------
            date = str
                date in format of "%Y-%m-%d"
            time = str
                time in format of "%H:%M:%S.%f"
            """         
            self._update_header("forecastDate", {"date": date, "time":time}) 

        def approvedDate(self, date, time):
            """
            Since version 1.20. Returns the time that simulated forecast was made current. In case of no longer current then the original approved time is returned.
            
            Parameters
            ----------
            date = str
                date in format of "%Y-%m-%d"
            time = str
                time in format of "%H:%M:%S.%f"
            """        
            self._update_header("approvedDate", {"date": date, "time":time})                

        def missVal(self, value):
            """
            Missing value definition for this TimeSeries. Defaults to NaN if left empty
            
            Parameters
            ----------
            value = float
                missing value for timeseries
            """        
            self._update_header("missVal", value)         

        def longName(self, value):
            """
            Optional long (descriptive) name
            
            Parameters
            ----------
            value = str
                descriptive name
            """        
            self._update_header("longName", value)                 

        def stationName(self, value):
            """
            Station name
            
            Parameters
            ----------
            value = str
                name of station
            """        
            self._update_header("stationName", value)                 

        def lat(self, value):
            """
            Latitude of station
            
            Parameters
            ----------
            value = float
                latitude of station
            """        
            self._update_header("lat", value)

        def lon(self, value):
            """
            Longitude of station
            
            Parameters
            ----------
            value = float
                longitude of station
            """        
            self._update_header("lon", value)

        def x(self, value):
            """
            X coordinate of station
            
            Parameters
            ----------
            value = float
                x coordinate of station
            """      
            self._update_header("x", value)

        def y(self, value):
            """
            Y coordinate of station
            
            Parameters
            ----------
            value = float
                y coordinate of station
            """        
            self._update_header("y", value)

        def z(self, value):
            """
            Z coordinate of station. From version 1.16 this optional element is only written when available. In 1.15 and earlier z=0.0 is used when z is not defined
            
            Parameters
            ----------
            value = float
                z coordinate of station
            """        
            self._update_header("z", value)

        def units(self, value):
            """
            Optional string that identifies the units used
            
            Parameters
            ----------
            value = str
                string containing the units of the timeseries
            """        
            self._update_header("units", value)

        def sourceOrganisation(self, value):
            """
            Name of source organisation
            
            Parameters
            ----------
            value = str
                optional name of source organisation
            """        
            self._update_header("sourceOrganisation", value)

        def sourceSystem(self, value):
            """
            Name of source system
            
            Parameters
            ----------
            value = str
                optional name of source system
            """         
            self._update_header("sourceSystem", value)

        def fileDescription(self, value):
            """
            Description of (the content of) this file
            
            Parameters
            ----------
            value = str
                optional file content description
            """        
            self._update_header("fileDescription", value)        

        def creationDate(self, value):
            """
            Optional element that maybe used by third parties. The element is not used by FEWS. It is neither written nor read.
            
            Parameters
            ----------
            value = str
                date in format of "%Y-%m-%d"
            """        
            self._update_header("creationDate", value)

        def creationTime(self, value):
            """
            Optional element that maybe used by third parties. The element is not used by FEWS. It is neither written nor read.
            
            Parameters
            ----------
            value = str
                time in format of "%H:%M:%S.%f"
            """        
            self._update_header("creationTime", value)

        def region(self, value):
            """
            Code/description of the region. Needed if the id"s can be the same in different regions.
            
            Parameters
            ----------
            value = str
                region id
            """        
            self._update_header("region", value)

        def thresholds(self, threshold_id, name, label):
            """
            Parameters
            ----------
            value = boolean
                true or false
            """        
            self._update_header("thresholds", {"id": threshold_id, "name":name, "label": label})    

    @InnerClassDescriptor
    class _Events(object): 
            
        def _update_events(self, value):
            try:
                self._outer.view["timeSeries"][0]["events"] = value
            except KeyError as e:
                if e.args[0] == "events":
                    self._outer.view["timeSeries"][0]["events"] = value    
                if e.args[0] == "timeSeries":
                    self._outer.view["timeSeries"]= []
                    self._outer.view["timeSeries"].append({})
                    self._outer.view["timeSeries"][0]["events"] = value
            
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
                raise ValueError("index does not exist or not contains datetime objects")                  
            if not value.index.name:
                index_name = "index"
            else:
                index_name = value.index.name

            value = value.reset_index()
            value.rename(columns={index_name: "datetime"}, inplace=True)
        
            # only select column names that are accepted
            given_names = list(value.columns)
            given_names.remove('datetime')
            accepted_names = ["value", "minValue", "maxValue", "flag", "flagSource", "comment", "user"]
            taken_names = list(set(given_names) & set(accepted_names))
            inv_names = (list(set(given_names) - set(taken_names)))
            if len(inv_names):
                inv_message = " The following column names are ignored: '{}'. \n Only the following column names are accepted: '{}''".format(
                    "', '".join(inv_names), 
                    "', '".join(accepted_names)
                )
                logging.warning(inv_message)

            # parse to row oriented json
            value.set_index('datetime', inplace=True)
            value_json = value[taken_names]

            # parse to Pi-json object
            self._update_events(value_json)

# class containing utils functions
class Utils(object):
    @staticmethod
    def addFilter(self, child):
        setattr(self.Filters, child["id"].replace(".", "_"), {"id": child["id"],
                                                              "name": child.name.cdata,
                                                              "description": child.description.cdata})

    @staticmethod
    def event_client_datetime(event, tz_server, tz_client="Europe/Amsterdam"):
        """
        Get datetime object in client time of an XML Element named event with attributes date and time
        input:
        event     : XML Element named event [eg: obj.TimeSeries.series.event[0]]
        tz_server : datetime abbreviation of the server timezone [eg: "Etc/GMT"]
        tz_client : datetime abbreviation of the client timezone [eg: "Europe/Amsterdam"]

        return
        event_client_time : an datetime object of the event in client timezome

        """
        # convert XML element date string to integer list
        event_server_date = list(
            map(int, event["date"].split("-")))  # -> [yyyy, MM, dd]
        event_server_time = list(
            map(int, event["time"].split(":")))  # -> [HH, mm, ss]

        # define server time
        server_time = datetime(event_server_date[0], event_server_date[1], event_server_date[2],
                               event_server_time[0], event_server_time[1], event_server_time[2],
                               tzinfo=pytz.timezone(tz_server))
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

    
# -------------------------------------------- #
# here start the functions    
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    dom_string = reparsed.toprettyxml(indent="  ", newl='\n')
    dom_string = '\n'.join([s for s in dom_string.splitlines() if s.strip()])
    
    return reparsed.toprettyxml(indent="  ")

def set_pi_timeseries(prefill_defaults=False):
    """
    Create a new query object.
    Returns a new :class:`DataQuery` instance appropriate for this endpoint.
    
    Returns
    -------
    valid : bool
        Whether `query` is valid.
    """
    if prefill_defaults == True:
        s_dflt = SetPiTimeSeries()
        s_dflt.write.root.timeZone("0.0")
        s_dflt.write.root.version("1.22") 
        s_dflt.write.header.timeSeriesType("instantaneous") 
        return s_dflt
    else:
        return SetPiTimeSeries()
        
def read_timeseries_response(getTimeSeries_response, tz_client, header="longform"):
    """
    function to parse raw xml into python objects
    
    Parameters
    ----------
    getTimeSeries_response : stringIO object
        zeep returned object from a getTimeSeries* query
    header : str
        how to parse the returned header object. Choose from:
        - "multiindex", tries to parse the header into a single pandas.DataFrame where the header is contained as multi-index.
        - "dict", parse the events of the response in a pandas.DataFrame and the header in a seperate dictionary
    """
    
    utils = Utils()
    
    if header in ["multiindex", "longform"]:
        getTimeSeries_json = parse_raw(getTimeSeries_response)

        timeZoneValue = int(
            float(getTimeSeries_json.TimeSeries.timeZone.cdata))
        if timeZoneValue >= 0:
            timeZone = "Etc/GMT+" + str(timeZoneValue)
        else:
            timeZone = "Etc/GMT-" + str(timeZoneValue)

        # empty dictionary to fill with dictionary format of each row
        # method adopted to avoid appending to pandas dataframe
        event_attributes = ["value", "flag", "user"]
        rows_ts_dict = {}
        rows_latlon_list = []

        timeZoneValue = int(
            float(getTimeSeries_json.TimeSeries.timeZone.cdata))
        # Etc/GMT* follows POSIX standard, including counter-intuitive sign change: see https://stackoverflow.com/q/51542167/2459096
        if timeZoneValue >= 0:
            timeZone = "Etc/GMT-" + str(timeZoneValue)
        else:
            timeZone = "Etc/GMT+" + str(timeZoneValue)

        # start iteration
        for series in getTimeSeries_json.TimeSeries.series:
            # initiate empty lists
            moduleInstanceId = []
            qualifierId = []
            locationId = []

            stationName = []
            parameterId = []
            units = []

            event_datetimes = []
            event_values = []
            event_user = []            
            event_flags = []

            # collect metadata
            # GET qualifierId
            try:
                qualifierId.append(series.header.qualifierId.cdata)
            except AttributeError as e:
                qualifierId.append("")
                # print("warning:", e)

            # GET moduleInstanceId
            try:
                moduleInstanceId.append(series.header.moduleInstanceId.cdata)
            except AttributeError as e:
                moduleInstanceId.append("")
                print("warning:", e)

            # GET locationId
            try:
                locationId.append(series.header.locationId.cdata)
            except AttributeError as e:
                print("warning:", e)

            # GET lat
            try:
                lat = float(series.header.lat.cdata)
            except AttributeError as e:
                print("warning:", e)

            # GET lon
            try:
                lon = float(series.header.lon.cdata)
            except AttributeError as e:
                print("warning:", e)

            # GET stationNames
            try:
                stationName.append(series.header.stationName.cdata)
            except AttributeError as e:
                print("warning:", e)

            # GET parameterId
            try:
                parameterId.append(series.header.parameterId.cdata)
            except AttributeError as e:
                print("warning:", e)

            # GET units
            try:
                units.append(series.header.units.cdata)
            except AttributeError as e:
                print("warning:", e)

            if hasattr(series, "event"):
                # GET data values
                for event in series.event:
                    event_datetimes.append(utils.event_client_datetime(
                        event, tz_server=timeZone, tz_client=tz_client))
                    event_values.append(float(event["value"]))
                    event_flags.append(int(event["flag"]))
                    # temp fix for user
                    try:
                        event_user.append(str(event["user"]))
                    except:
                        pass
                        

            # PUT timeseries info into row dictionary
            # temporary solution to include user information
            if len(event_user):
                dataValuesFlags = [event_values, event_flags, event_user]
            else:
                dataValuesFlags = [event_values, event_flags]
            
            multiColumns = pd.MultiIndex.from_product([
                moduleInstanceId, qualifierId, parameterId, units, 
                locationId, stationName, event_attributes],
                names = ["moduleInstanceIds", "qualifierIds", "parameterIds", "units", 
                       "locationIds", "stationName", "event_attributes"])
            df_ts_dict = pd.DataFrame(
                dataValuesFlags, index=multiColumns, columns=event_datetimes).T.to_dict()

            # PUT timeseries row in dictionary of rows
            rows_ts_dict.update(df_ts_dict)

            # PUT latlon/location row in dictionary of rows
            rows_latlon_list.append(
                {"stationName": stationName[0], "Lat": lat, "Lon": lon})

        # CREATE dataframe of timeseries rows dictionary
        df_timeseries = pd.DataFrame(rows_ts_dict)

        # reset the multiIndex and create a stacked DataFrame and convert to row-oriented JSON object
        df_timeseries = df_timeseries.stack([0, 1, 2, 3, 4, 5]).rename_axis(
            ["date", "moduleInstanceId", "qualifierId", "parameterId", "units", "locationId", "stationName"])

        # Temp fix for to pop empty user column if only None
        df_timeseries.loc[df_timeseries['user'].str.match('None'), 'user'] = None 
        df_timeseries = df_timeseries.T.dropna().T        
        
        if header == "longform":
            df_timeseries = df_timeseries.reset_index(level=["moduleInstanceId", "qualifierId", "parameterId", "units", "locationId", "stationName"])        
        
    elif header == "dict":
        raise("option 'dict' for parameter 'header' is not yet implemented")
        

        
    return df_timeseries
