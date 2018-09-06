from .io.soap_fewspi import pi

__doc__ = """package for accessing fewspi service"""
__version__ = '0.6.0'

pi = pi()

if __name__ == '__main__':
    try:
        # for command line requests
        fire.Fire(pi)
        #pi = pi()
    except:
        # for jupyter notebooks
        #pi = pi()
        pass
