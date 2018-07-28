# hkvfewspy
python wrapper for fews-pi sevices

# usage
```
import hkvfewspy as hkv
# set client
pi = hkv.pi
pi.setClient(wsdl='http://localhost:8081/FewsPiService/fewspiservice?wsdl')
```

# available functions
- setClient
- setQueryParameters
- getFilters
- getParameters
- getTimeSeries
- getTimeZoneID
- getAvailableTimeZones


# example using setQueryParameters function`

```python
query = pi.setQueryParameters(prefill_defaults=True)

query.parameterIds(['m3.minDepth.cut'])
query.moduleInstanceIds(['pr.minDepth.cutfill.volopp.setfill'])
query.locationIds(['bv.1.7.2.3.2'])
query.startTime(datetime(2018,1,1))
query.endTime(datetime.now())
query.clientTimeZone('Europe/Amsterdam')

df, entry = pi.getTimeSeries(queryParameters=query, setFormat='df')
df.head()
```

# notebook
in the notebook folder is placed a jupyter notebook with more examples.
the module has been tested against both embedded and public fews-pi webservices in python2 and python3.

# build from source
cmd into the root directory (there were `setup.py` is located)
and type `pip wheel . .` from the commandline.

# build distribution directory
`python setup.py sdist bdist_wheel`

# upload to PyPI
from root directory
`twine upload --repository-url https://upload.pypi.org/legacy/ dist/*`
username
password

this will update the wheel which can be installed through `pip install hkvfewspy`
