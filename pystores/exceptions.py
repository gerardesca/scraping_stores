"""
Global exception and warning classes.
"""

class ImproperlyConfigured(Exception):
    """Class is somehow improperly configured"""
    pass


class InvalidReturnTypeException(Exception):
    """Function return an invalid value(s)"""
    pass
