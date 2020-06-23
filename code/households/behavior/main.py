"""Defining the overarching Rule class.
"""
from households import inspect, main


class Rule(object):
    """An behavior run each year by a person. Most generic form.
    
    """
    
    def __init__(self):
        pass
    
    def __verify_callable__(self,rule,argnum = [1]):
        """Check that rule is callable and has only one non-default argument.
        
        Parameters
        ---------
        rule : callable
            A rule to check that it is callable and has the right number of arguments
        argnum : int or list of int
            A list of acceptable integer values for arguments passed to rule
            
        Returns
        ------
        bool
            True if properly formatted, False if not + raises an error
        """
        #Check that argnum is properly formatted
        if type(argnum) == list:
            #If list, make sure entries are int
            if all([type(x) == int for x in argnum]) == False:
                raise ValueError('argnum list not of ints')
        elif type(argnum) == int:
            argnum = [argnum]
        else:
            raise TypeError('argnum neither int nor list of int')
        #Now check that the function is callable and takjes teh right number of 
        ## arguments
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
    
    def __verify_agetable__(self,agetable):
        """Check that agetable is AgeTable."""
        if isinstance(agetable, main.AgeTable) == False:
            raise TypeError('agetable not of type main.AgeTable')
            return False
        else:
            return True

