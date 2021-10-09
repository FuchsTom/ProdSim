from typing import Dict, Any, List, Callable, Tuple
from random import normalvariate, random, uniform

from numpy.random import poisson, exponential, lognormal, chisquare, standard_t, binomial

from prodsim.exception import NotSupportedParameter, BlockedIdentifier, InvalidType


class Helper:
    """Contains all helper functionalities needed in the package prodsim

    At the moment, only the functions to convert the distribution functions into concrete expressions are located here.
    But to outsource future functionalities this class was created.

    """

    # ---- determinate attributes -------------------------

    # Cache the identifiers and the corresponding functions of the user-defined distributions for a simulation run
    __user_defined_switch_dict: Dict[str, Callable] = {}

    # Since there will be switch-case structures only from Python 3.10, we have to fall back on the switch-dict
    # structure here
    _switch_dict: Dict[str, Callable] = {'n': lambda x: normalvariate(x[1], x[2]),
                                         'f': lambda x: x[1],
                                         'b': lambda x: int(random() < x[1]),
                                         'u': lambda x: uniform(x[1], x[2]),
                                         'p': lambda x: poisson(x[1]),
                                         'e': lambda x: exponential(x[1]),
                                         'l': lambda x: lognormal(x[1], x[2]),
                                         'c': lambda x: chisquare(x[1]),
                                         't': lambda x: standard_t(x[1]),
                                         'i': lambda x: binomial(x[1], x[2])
                                         }

    @staticmethod
    def clear_ud_switch_dict():
        """Flushes the dictionary with the user-defined distributions

        This method is called between two simulation calls to avoid BlockedIdentifier Errors

        """

        Helper.__user_defined_switch_dict = {}

    @staticmethod
    def add_user_distribution(function_list: List[Tuple[str, Callable]]):
        """Inserts a user-defined functions into the '__user_defined_switch_dict' attribute"""

        for func_tuple in function_list:

            # Check whether the identifier is already assigned
            if func_tuple[0] in Helper._switch_dict:
                raise BlockedIdentifier("the identifier {} can't be used since it is predefined.".format(func_tuple[0]))

            # Add the user defined function to the corresponding attribute
            Helper.__user_defined_switch_dict[func_tuple[0]] = lambda x: func_tuple[1](*x[1:])

    @staticmethod
    def determinate_attr(dict_: Dict[str, Any]) -> Dict[str, Any]:
        """Converting a dictionary with attribute names and a respective distribution into a dictionary with attribute
        names and concrete values of these attributes.

        """

        # Dictionary with the attribute names and concrete characteristics of these attributes
        temp_dict: Dict[str, Any] = {}

        for attr_ in dict_.items():

            try:
                # Case: predefined distribution
                temp_dict[attr_[0]] = Helper._switch_dict[attr_[1][0]](attr_[1])
            except KeyError:
                try:
                    # Case: user-defined distribution
                    temp_dict[attr_[0]] = Helper.__user_defined_switch_dict[attr_[1][0]](attr_[1])
                except KeyError:
                    raise NotSupportedParameter("The identifier '{ident}' isn't a supported for attributes."
                                                "".format(ident=attr_[1][0]))
            except (TypeError, ValueError):
                raise InvalidType("The attribute '{attr}', might not be correct.".format(attr=attr_[0]))

        return temp_dict

    # ---- future functionality ---------------------------
