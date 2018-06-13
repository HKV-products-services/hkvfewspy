# hkvfewspy
python wrapper for fews-pi sevices

version 0.3.0

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


example of a net getTimeSeries call

startTime = datetime(2017,1,1)
endTime =  datetime.now()

params = dict(
    locationIds=['M_40000304'],
    parameterIds=['H.meting'],
    startTime=startTime,
    endTime=endTime,
    clientTimeZone = 'Etc/GMT+1',
    showStatistics='true',
    convertDatum='true',
    forecastSearchCount =0,
    importFromExternalDataSource='false',
    omitMissing ='false',
    onlyHeaders ='false',
    onlyManualEdits ='false',
    showEnsembleMemberIds ='false',
    showThresholds ='false',
    useDisplayUnits ='false'
)

df, entry = pi.getTimeSeries(params, setFormat='df')

in the notebook folder is placed a jupyter notebook with more examples.
the module has been tested against both embedded and public fews-pi webservices in python2 and python3.

# build from source
cmd into the root directory (there were `setup.py` is located)
and type `pip wheel . .` from the commandline.

this will recreate the wheel which can be installed through `pip install hkvfewspy`
