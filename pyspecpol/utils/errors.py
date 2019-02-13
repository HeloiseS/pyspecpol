import warnings

### Variables ####


### Custom checks and warnings ###

def _warn_if_list(parameters):
    """ Checks if a (list of) parameter(s) is a list and raises a warning"""
    try:
        for param in parameters:
            if isinstance(param, list): warnings.warn(" You are parsing a list. "
                                                      "Operations on lists may fail -- use arrays.")
    except TypeError:
        if isinstance(parameters, list): warnings.warn(" You are parsing a list. "
                                                       "Operations on lists may fail -- use arrays.")