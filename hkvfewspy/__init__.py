from .io.soap_fewspi import PiSoap
from .schemas.timeseries import FewsTimeSeries, FewsTimeSeriesCollection

# currently PiSoap maps to Pi
# in future user should decide which webservice to use
Pi = PiSoap

__doc__ = """package for accessing fewspi service"""
__version__ = "0.6.3"

