## hkvfewspy
python wrapper for fews-Pi sevices

## installation
make sure you have all dependencies installed, and then install `hkvfewspy`.
```bash
conda install geopandas 
pip install hkvfewspy
```

## usage

SOAP backend

```python
import hkvfewspy as hkv
pi = hkv.Pi() # or hkv.Pi(protocol='soap')
pi.setClient(wsdl='http://localhost:8081/FewsPiService/fewspiservice?wsdl')
```

REST backend

```python
import hkvfewspy as hkv
pi = hkv.Pi(protocol='rest')
pi.setUrl(url='http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/')
```

## changelog
0.7

added REST protocol including
* setUrl
* getFilters
* getParameters
* getTimeSeries
* getTimeZoneID
* postTimeSeries

initiate using:
* `pi = hkv.Pi(protocol='rest')` 
* default protocol is `soap` for backwards compatibilty

* see this [notebook](https://nbviewer.jupyter.org/github/HKV-products-services/hkvfewspy/blob/master/notebooks/test%20REST%20endpoint.ipynb) for an example 

0.6.3
- removed geopandas as required dependencies
- setPiTimeSeries now includes miliseconds (BUG: FEWS doesn't support this yet)


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

