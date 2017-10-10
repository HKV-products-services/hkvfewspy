# hkvfewspy
python wrapper for fews-pi sevices

# usage
`from hkvfewspy.io.fewspi import pi`

the following functions are available from within the module
- setClient
- getFilters
- getParameters
- getTimeSeries
- getTimeZoneID

the module has been tested against both embedded and public fews-pi webservices in python2 and python3.

# build from source
cmd into the root directory (there were `setup.py` is located)
and type `pip wheel . .` from the commandline.

this will recreate the wheel which can be installed through `pip install hkvfewspy`
