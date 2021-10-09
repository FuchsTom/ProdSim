"""Bundles all exceptions and warnings used in the package prodsim"""

class InvalidValue(Exception):
    """ Raises when a value is not within the permissible range """
    pass

class InvalidType(Exception):
    """ Raises when a value has the wrong type """
    pass

class MissingParameter(Exception):
    """ Raised when a required parameter is missing """
    pass

class MissingAttribute(Exception):
    """ Raises when a not defined attribute is used """
    pass

class NotSupportedParameter(Exception):
    """ Raised when a not defined parameter is passed """
    pass

class FileNotFound(Exception):
    """ Raised when a file couldn't be found """
    pass

class InvalidFormat(Exception):
    """ Raises when a parameter has the wrong format """

class UndefinedFunction(Exception):
    """ Raises when a function isn't defined """
    pass

class UndefinedObject(Exception):
    """ Raises if an referenced object is not defined """
    pass

class InvalidFunction(Exception):
    """ Raises when a function is not valid """
    pass

class InvalidYield(Exception):
    """ Raises when a generator function doesn't yield the correct types """

class InvalidSignature(Exception):
    """ Raises when a signature  """

class ToManyArguments(Exception):
    """ Raises, when to many arguments are passed """
    pass

class MissingData(Exception):
    """ Raises, when required data is missing """
    pass

class BlockedIdentifier(Exception):
    """ Raises, when an identifier is already blocked """
    pass

class InfiniteLoop(Exception):
    """ Raises, when a function contains an infinite loop """

class BadType(Warning):
    """ when a parameter has a bad type """
    pass

class BadSignature(Warning):
    """ when a argument has not the expected name """
    pass

class BadYield(Warning):
    """ when a yield is possible but can lead to problems """
    pass

class NotDefined(Warning):
    """ when a non pre defined identifier is used """
    pass
