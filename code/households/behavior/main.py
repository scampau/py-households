"""Defining the overarching Rule class.
"""
from households import inspect, main


class Rule(object):
    """An behavior run each year by a person. Most generic form.
    
    """
    
    def __init__(self):
        pass
    
    def __verify_rule__(self,rule,argnum = [1]):
        """Check that rule is callable and has only one non-default argument.
        
        Parameters
        ---------
        rule : callable
            A rule to check that it is callable and has the right number of arguments
        argnum : list of int
            A list of acceptable integer values for arguments passed to rule
            
        Returns
        ------
        bool
            True if properly formatted, False if not + raises an error
        """
        if callable(rule) == True:
            #Now count non-default arguments, must be 0 or 1
            sig = inspect.signature(rule)
            if sum([y.default == inspect._empty for y in sig.parameters.values()]) in argnum:
                return True
            else:
                raise ValueError(rule.__name__ + ' has the wrong number of non-default arguments')
                return False
        else:
            raise TypeError('rule is not callable')
            return False
        
    def __verify_person__(self,person):
        """Check that person is a Person
        """
        if isinstance(person,main.Person) == False:
            raise TypeError('person not an instance of Person')
            return False
        else:
            return True
    
    def __verify_house__(self,house):
        """Check that house is a House."""
        if isinstance(house,main.House) == False:
            raise TypeError('house not an instance of House')
            return False
        else:
            return True

