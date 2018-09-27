## hkvfewspy
python wrapper for fews-Pi sevices

## installation
through pip
```bash
pip install hkvfewspy
```

## usage
```python
import hkvfewspy as hkv
pi = hkv.Pi()
pi.setClient(wsdl='http://localhost:8081/FewsPiService/fewspiservice?wsdl')
```

## available functions
- setClient
- setQueryParameters
- setPiTimeSeries
- getFilters
- getParameters
- getTimeSeries
- getTimeZoneID
- getAvailableTimeZones
- getWorkflows
- getTaskRunStatus
- runTask
- putTimeSeriesForFilter


## notebook
in the notebook folder are placed several jupyter notebooks with more examples.
the module has been tested against both embedded and public fews-Pi webservices in python2 and python3.

## credits
HKVFEWSPY is written by:
- Mattijn van Hoek <m.vanhoek@hkv.nl>
- Johan Ansink <j.ansink@hkv.nl>
- Raoul Collenteur <r.collenteur@artesia-water.nl>
- Davíd Brakenhoff <d.brakenhoff@artesia-water.nl>

## compiling notes

#### build distribution directory
`python setup.py sdist bdist_wheel`

#### upload to PyPI
from root directory
`twine upload --repository-url https://upload.pypi.org/legacy/ dist/*`
username
password

this will update the wheel which can be installed through `pip install --upgrade hkvfewspy` 

