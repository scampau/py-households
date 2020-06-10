"""Household fragmentation processes.

These functions are run by households each year to decide whether the household
needs to split apart into new households. This is to model conflicts such as
brother-brother conflicts after the death of the patriarch.

Each fragmentation function will need to take a household and determine 
whether anyone in that household needs to leave. If they do, move them.

"""

from households import np, rd, scipy, nx, plt, kinship, residency, behavior
from households.identity import *

print('importing fragmentation')

class FissionRule(object):
    """Defining how a household can break apart.
    
    Fission rules consist of a context for fragmentation, a way to identify
    who will leave, and a destination for them.
    
    Parameters
    ----------
    check_house : callable
        Takes a house, returns who will leave if it will fragment, False otherwise. Can 
        include randomness.
    destination : callable
        Takes a house and a group and identifies the house where they will move.
        The fission rule does the relocation of people in who.
    
    """
    def __init__(self, check_house, destination):
        #make sure all are callable and take the right number of arguments
        for r, n in zip([check_house, destination],[1,2]):
            if self.__verify_rule__(r,[n]) == True:
                pass
            else:
                raise ValueError('wrong number of arguments for '+str(r.__name__))
        self.__check_house = check_house
        self.__destination = destination
    
    def __call__(self, house):
        """Determine if a household will fragment, and carry it out if so.

        Parameters
        ----------
        house : main.House
            The house in question.

        Returns
        -------
        True if fission occurred, else False.

        """
        if self.__verify_house__(house) == False:
            raise TypeError('house not an instance of House')
        #if it really is a house, then first identify whether it will fragment
        who_leaves = check_house(house)
        if who_leaves != False:
            #Yes, the household will fragment
            if len(who_leaves) == 0:
                #No one identified to leave specifically, so no fragmentation
                return False
            else:
                #Fragmentation happens, so identify destination
                goto = destination(house, who_leaves)
                for p in who_leaves:
                    behavior.inheritance.move_person_to_new_house(p,goto)
                return True
        else:
            return False
    
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
    
    def __verify_house__(self,house):
        """Check that house is a House
        """
        if isinstance(house,main.House) == False:
            raise TypeError('house not an instance of House')
            return False
        else:
            return True



#check household conditions
def check_household_overcrowded(house):
    """Returns whether the household is overcrowded.
    
    Parameters
    ----------
    house : main.House
        The house to check.

    Returns
    -------
    bool

    """
    pass
    
def check_household_never_fragment(house):
    """Always returns that the household doesn't fragment.
    
    Parameters
    ----------
    house : main.House
        The house to check.

    Returns
    -------
    False

    """
    #Wow, that was easy!
    return False

def check_household_younger_brothers_disinherited(house,age):
    """Returns whether the household includes younger disinherited brothers.
    
    Parameters
    ----------
    house : main.House
        The house to check.
    age : int
        The age of majority (marriage often) for determining whether an adult 
        brother feels the pressure to leave and create a new household.

    Returns
    -------
    bool
        Whether the household will fragment

    """
    pass

#destination rules

def destination_random_house_same_village(house, who_leaves):
    """Find a suitable house in the same village

    Parameters
    ----------
    house : TYPE
        DESCRIPTION.
    who_leaves : TYPE
        DESCRIPTION.

    Returns
    -------
    house

    """
    
def destination_radnom_house_random_village(house, who_leaves, weighting = "population"):
    """Pick a random house in a random other village

    Parameters
    ----------
    house : TYPE
        DESCRIPTION.
    who_leaves : TYPE
        DESCRIPTION.
    weighting : ['population','empty_houses','equal']
        What weighting to use for the random village selection

    Returns
    -------
    house

    """
    pass

def destination_random_house_specific_village(house, who_leaves, village):
    """Select a random house in a particular village (e.g. a destination community)

    Parameters
    ----------
    house : TYPE
        DESCRIPTION.
    who_leaves : TYPE
        DESCRIPTION.
    village : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    pass



#old fragmentation functions
def no_fragmentation(house):
    """No fragmentation rule.
    
    A household with this rule will never fragment.
    
    Parameters
    ---------
    house : House
        The household which won't fragment.
    """
    pass

def brother_loses_out(house,age):
    """Non-owner adult brothers leave when the oldest brother inherits the house. 
    
    A (younger) adult brother who just lost out on the family inheritance leaves the
    house along with his family. Otherwise, everyone stays put.
    
    Parameters
    ---------
    house : House
        The household to check to see if it will fragment.
    age : int
        The age of majority (marriage often) for determining whether an adult 
        brother feels the pressure to leave and create a new household.
    """
    # Check whether any brothers are there
    if house.people != [] and house.owner != None:    
        siblings = kinship.get_siblings(house.owner)
        if siblings != []:
            siblings = [x for x in siblings if x.sex == male and x.age >= age and x.lifestatus == alive]
            if len(siblings) > 0:
                for s in siblings:
                    #For each brother who lives in the house
                    if s in house.people:
                        #If there is another brother over the age of majority who is
                        ## not hte ownerwho lives there that person ( and their family)
                        ## moves out
                        # Pick a new house
                        new_house = behavior.locality.get_empty_house(house.has_community.houses)
                        if new_house != None:
                            # Identify their family and move them
                            behavior.inheritance.move_family_to_new_house(s,new_house)
                        else:
                            # There is no new house, so stay put.
                            pass               

def house_gets_crowded(house):
    """Over-capacity housing prompts families to relocate.
    
    A house that exceeds its capacity gets rid of 1) non-kin of the owner,
    2) more distant kin of the owner.
    
    Parameters
    ---------
    house : House
        The house to check for overcrowding.
    """
    pass #To be continued