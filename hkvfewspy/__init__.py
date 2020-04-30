from .io.soap_fewspi import PiSoap
from .io.rest_fewspi import PiRest
from .schemas.timeseries import FewsTimeSeries, FewsTimeSeriesCollection

# currently PiSoap maps to Pi
# in future user should decide which webservice to use

def Pi(protocol="soap"):
    """
    set the endpoint protocol
    
    Parameters
    ----------
    protocol : str
        choose between 'soap' or 'rest' 
        defaults to 'soap' to remain backwards compitability
    """

    if protocol == 'rest':
        Pi = PiRest()
    elif protocol == 'soap':
        Pi = PiSoap()
    else:
        raise ValueError('wrong protocol')
    return Pi


__doc__ = """package for accessing fewspi service"""
__version__ = "0.9"

