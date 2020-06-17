"""Defines categorical identities that Persons can have, such as sex.

Because identity is key to a social simulation, the identities module defines
different classes that can be used to identify and discriminate between agents
who have contrasting identities. These identities include:

    * sex
    * marriage status
    * life status

Each identity typically includes attributes for use in narrative, such as 
adjective, noun, possessive, etc. By convention these are all lowercase and 
can be capitalized when need be by stirng functions.

Further planned identities include social status, race, ethnicity, gender,
and sexuality, to allow more nuanced simulations of diverse societies.

This module is a pre-requisite for almost every other module.

See Also
--------
narrative
    The module for creating legible text and histories from simulation runs, 
    and which often takes identities as inputs from Person objects.
"""

print('Importing identity')


class Sex:
    """The class for sex objects.
    
    Parameters
    ----------
    adjective : str
        The adjective of this sex for use in text-based output.
    noun : str
        The noun for use in text-based output.
    possessive : str
        The possessive to use for text-based output.
        
    Attributes
    ----------
    adjective : str
        The adjective of this sex for use in text-based output.
    noun : str
        The noun for use in text-based output.
    possessive : str
        The possessive to use for text-based output.
    """
    
    def __init__(self,adjective,noun,possessive):
        self.adjective = adjective
        self.noun = noun
        self.possessive = possessive
    @property
    def adjective(self):
        return self.__adjective
    
    @adjective.setter
    def adjective(self,x):
        if type(x) == str:
            self.__adjective = x
        else:
            self.__adjective = ''
            
    @property
    def noun(self):
        return self.__noun
    
    @noun.setter
    def noun(self,x):
        if type(x) == str:
            self.__noun = x
        else:
            self.__noun = ''
    
    @property
    def possessive(self):
        return self.__possessive
    
    @possessive.setter
    def possessive(self,x):
        if type(x) == str:
            self.__possessive = x
        else:
            self.__possessive = ''
    
    
female = Sex('female','woman','her')
male = Sex('male','man','his')


class LifeStatus:
    """The class for being alive or dead.
    
    Parameters
    ----------
    adjective : str
        The adjective of this sex for use in text-based output
    """
    
    def __init__(self,adjective):
        self.adjective = adjective
    
    @property
    def adjective(self):
        return self.__adjective
    
    @adjective.setter
    def adjective(self,x):
        if type(x) == str:
            self.__adjective = x
        else:
            self.__adjective = ''

alive = LifeStatus('living')
dead = LifeStatus('dead')

class MarriageStatus:
    """The class for being married, unmarried, or ineligible.
    
    Parameters
    ----------
    adjective : str
        The adjective of this sex for use in text-based output
 
    """
    
    def __init__(self,adjective):
        self.adjective = adjective
    @property
    def adjective(self):
        return self.__adjective
    
    @adjective.setter
    def adjective(self,x):
        if type(x) == str:
            self.__adjective = x
        else:
            self.__adjective = ''

ineligible = MarriageStatus('ineligible')
unmarried = MarriageStatus('unmarried')
married = MarriageStatus('married')
widowed = MarriageStatus('widowed')

