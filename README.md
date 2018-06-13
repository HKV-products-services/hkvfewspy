# hkvfewspy
python wrapper for fews-pi sevices

# usage
`from hkvfewspy.io.fewspi import pi`

the following functions are available from within the module
- setClient
- getFilters
- getParameters
- getTimeSeries
- getTimeSeriesForFilter2 ! this is the 'v0.2.2 getTimeSeries'
- getTimeZoneID
- getAvailableTimeZones


`example of a net getTimeSeries call`

```python
startTime = datetime(2017,1,1)
endTime =  datetime.now()

queryParameters = dict(
    convertDatum='true',
    locationIds=['M_40000304'],
    parameterIds=['H.meting'],
    startTime=startTime,
    endTime=endTime,
    clientTimeZone = 'Etc/GMT+1',
    showStatistics='true',
    forecastSearchCount =0,
    importFromExternalDataSource='false',
    omitMissing ='false',
    onlyHeaders ='false',
    onlyManualEdits ='false',
    showEnsembleMemberIds ='false',
    showThresholds ='false',
    useDisplayUnits ='false'
    piVersion='1.23'
)

df, entry = pi.getTimeSeries(queryParameters, setFormat='df')
df.head()
```

queryParameters is defined by following schema definition:
```xml
<xs:complexType name="queryParameters">
    <xs:sequence>
    	<xs:element name="clientTimeZone" type="xs:string"></xs:element>
        <xs:element name="convertDatum" type="xs:boolean"></xs:element>
        <xs:element name="endCreationTime" type="xs:dateTime" minOccurs="0"></xs:element>
        <xs:element name="endForecastTime" type="xs:dateTime" minOccurs="0"></xs:element>
        <xs:element name="endTime" type="xs:dateTime" minOccurs="0"></xs:element>
        <xs:element name="ensembleId" type="xs:string"></xs:element>
        <xs:element name="externalForecastTime" type="xs:dateTime" minOccurs="0"></xs:element>
        <xs:element name="filterId" type="xs:string" minOccurs="0"></xs:element>
        <xs:element name="forecastSearchCount" type="xs:string" minOccurs="0"></xs:element>
        <xs:element name="importFromExternalDataSource" type="xs:boolean"></xs:element>
        <xs:element name="locationIds" type="xs:string" nillable="true" minOccurs="0" maxOccurs="unbounded"></xs:element>
        <xs:element name="moduleInsatnceIds" type="xs:string" nillable="true" minOccurs="0" maxOccurs="unbounded"></xs:element>
        <xs:element name="omitMissing" type="xs:boolean"></xs:element>
        <xs:element name="onlyHeaders" type="xs:boolean"></xs:element>
        <xs:element name="parameterIds" type="xs:string" nillable="true" minOccurs="0" maxOccurs="unbounded"></xs:element>
        <xs:element name="piVersion" type="xs:string" minOccurs="0"></xs:element>
        <xs:element name="qualifierIds" type="xs:string" nillable="true" minOccurs="0" maxOccurs="unbounded"></xs:element>
        <xs:element name="showStatistics" type="xs:boolean"></xs:element>
        <xs:element name="showThresholds" type="xs:boolean"></xs:element>
        <xs:element name="startCreationTime" type="xs:dateTime" minOccurs="0"></xs:element>
        <xs:element name="startForecastTime" type="xs:dateTime" minOccurs="0"></xs:element>       
        <xs:element name="startTime" type="xs:dateTime" minOccurs="0"></xs:element>
        <xs:element name="useDisplayUnits" type="xs:boolean"></xs:element>
    </xs:sequence>
</xs:complexType>
```

in the notebook folder is placed a jupyter notebook with more examples.
the module has been tested against both embedded and public fews-pi webservices in python2 and python3.

# build from source
cmd into the root directory (there were `setup.py` is located)
and type `pip wheel . .` from the commandline.

this will recreate the wheel which can be installed through `pip install hkvfewspy`
