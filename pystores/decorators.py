from pystores.exceptions import InvalidReturnTypeException


def validate_data_to_csv(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not isinstance(result, list):
            raise InvalidReturnTypeException("The value is not a data type list")
        if not all(isinstance(item, dict) for item in result):
            raise InvalidReturnTypeException("The items are not a data type dict")
        return result
    return wrapper