"""Household mobility processes.

These functions are run by households each year to decide whether the household
needs to split apart into new households. This is to model conflicts such as
brother-brother conflicts after the death of the patriarch.

Each mobility function will need to take a household and determine 
whether anyone in that household needs to leave. If they do, move them.

"""

from households import np, rd, scipy, nx, plt, inspect, kinship, residency, behavior, main
from households.identity import *

print('importing mobility')

class MobilityRule(object):
    """Defining how and why people leave a household or a house.
    
    Mobility rules consist of a context for mobility, a way to identify
    who will leave, and a destination for them. They then move.
    
    Parameters
    ----------
    check_household : callable
        Takes a person, returns True if it their house will fragment, False otherwise. Can 
        include randomness.
    who_leaves_house : callable
        Takes a person, returns who will leave their house. If no eligible to leave, return []
    destination : callable
        Takes a house and a group to move and identifies the house where they will move.
        The mobility rule does the relocation of people in who.
    
    """
    def __init__(self, check_household, who_leaves_house, destination):
        #make sure all are callable and take the right number of arguments
        for r, n in zip([check_household, who_leaves_house, destination],[1,1,2]):
            if self.__verify_rule__(r,[n]) == True:
                pass
            else:
                raise ValueError('wrong number of arguments for '+str(r.__name__))
        self.__check_household = check_household
        self.__who_leaves_house = who_leaves_house
        self.__destination = destination
    
    def __call__(self, person):
        """Determine if a household will fragment, and carry it out if so.
        
        Parameters
        ----------
        house : main.House
            The house in question.
            
        Returns
        -------
        True if mobility/migration occurred, else False.
        
        """
        if self.__verify_person__(person) == False:
            raise TypeError('person not an instance of Person')
        #if it really is a house, then first identify whether it will fragment
        if self.__check_household(person) == True:
            #Yes, the household will fragment
            who_leaves = self.__who_leaves_house(person)
            if len(who_leaves) == 0:
                #No one identified to leave specifically, so no mobility
                return False
            else:
                #mobility happens, so identify destination
                house = person.has_house
                goto = self.__destination(house, who_leaves)
                for p in who_leaves:
                    move_person_to_new_house(p,goto)
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
    
    def __verify_person__(self,person):
        """Check that person is a Person
        """
        if isinstance(person,main.Person) == False:
            raise TypeError('person not an instance of Person')
            return False
        else:
            return True

class MobilityRuleMultiple(MobilityRule):
    """Chain multiple MobilityRules together; carried out in order
    
    """
    

#check household conditions
def check_household_overcrowded(person):
    """Returns whether the household is overcrowded.
    
    Parameters
    ----------
    person : main.Person
        The person whose house to check.

    Returns
    -------
    bool

    """
    if isinstance(person,main.Person):
        house = person.has_house
        if house == None:
            return False #This person doesn't have a house
        elif house.maxpeople < len(house.people):
            #The house is overcrowded
            return True
        else:
            #The house isn't overcrowded
            return False
    else:
        raise TypeError('person not Person')

        
def check_household_never_fragment(person):
    """Always returns that the household doesn't fragment.
    
    Parameters
    ----------
    person : main.Person
        The person whose house to check.

    Returns
    -------
    False

    """
    #Wow, that was easy!
    return False

def check_household_younger_brothers_disinherited(person,age):
    """Returns whether the person is a younger disinherited brother of the owner.
    
    Parameters
    ----------
    person : main.Person
        The person whose house to check.
    age : int
        The age of majority (marriage often) for determining whether an adult 
        brother feels the pressure to leave and create a new household.

    Returns
    -------
    bool
        Whether the household will fragment

    """
    if isinstance(person,main.Person):
        house = person.has_house
        if house == None:
            return False #This person doesn't live in a house right now
        #If not the owner but a brother is and this person is eligible to 
        ##marry/own property/is above the age of majority:
        if house.owner != person and house.owner in kinship.get_siblings(house.owner) and person.age >= age and person.sex == male:
            return True
        else:
            return False
    else:
        raise TypeError('person not Person')

#who_leaves
def leave_house_non_kin(person):
    """Recursively check for nuclear families. Return who isn't related to the rest.

    Parameters
    ----------
    person : main.Person
        The person whose house needs to be checked

    Returns
    -------
    list of main.Person

    """
    if isinstance(person,main.Person):
        house = person.has_house
        if house == None:
            return [] #This person doesn't live in a house right now
        #make a list of who will leave
        who_leaves = house.people.copy()
        #for every person in the house, check if they have coresident kin
        for p in house.people:
            fam = kinship.get_family(p)
            fam.remove(p)
            if any([f in house.people for f in fam]):
                who_leaves.remove(p)
        return who_leaves             
    else:
        raise TypeError('person not Person')  


def leave_house_young_adult_brothers(person, age):
    """Determine the family of a young adult disinherited brother

    Parameters
    ----------
    person : main.Person
        The person to check
    age : int
        Age of majority/when the person feels pressure to leave the house.

    Returns
    -------
    None.

    """
    if isinstance(person,main.Person):
        house = person.has_house
        if house == None:
            return [] #This person doesn't live in a house right now
        #If not the owner but a brother is and this person is eligible to 
        ##marry/own property/is above the age of majority:
        if house.owner != person and house.owner in kinship.get_siblings(house.owner) and person.age >= age and person.sex == male:
            who_leaves = kinship.get_family(person)
            #only move coresidential
            who_leaves = [p for p in who_leaves if p not in house.people]
            return who_leaves
        else:
            return []
    else:
        raise TypeError('person not Person')


def leave_house_noone(person):
    """Return that noone needs to leave
    
    """
    if isinstance(person,main.Person):
        return []
    else:
        raise TypeError('person not Person')
        
def leave_house_family(person):
    if isinstance(person,main.Person):
        family = kinship.get_family(person)
        return [f for f in family if f in person.has_house.people]
    else:
        raise TypeError('person not Person')
 
#To be implemented when economic migraiton is a possibility
# def leave_house_adult(person, age, sex = [male, female]):
#     """Identify whether an adult of a given sex (or either) will leave.
    
#     This is to aid in modelling economic migration; note that marriage status
#     is NOT a factor considered!

#     Parameters
#     ----------
#     person : main.Person
#         The person whose house needs to be checked

#     Returns
#     -------
#     main.Person

#     """
#     if isinstance(person,main.Person):
#         house = person.has_house
#         if house == None:
#             return [] #This person doesn't live in a house right now
        
#     else:
#         raise TypeError('person not Person')



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
    houses = who_leaves[0].has_community.houses
    possible_houses = [h for h in houses if len(h.people) == 0 and h.owner == None]
    if len(possible_houses) == 0:
        ## if no houses available
        return None
    else:
        return rd.choice(possible_houses)
    
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

#Functions for moving people, families, and entire households


def move_person_to_new_house(person,new_house):
    """Move an individual to a new house.
    
    Parameters
    ----------
    person : Person
        A Person who will be moved along with their co-resident family.
    new_house : House
        The new house into which they will be moved.    

    """
    if person.has_house == new_house:
        pass #do nothing, already lives there!
    else:
        old_house = person.has_house
        if person.lifestatus == dead:
            pass
        else:
            if old_house != None:
                old_house.remove_person(person)
            new_house.add_person(person)

def move_family_to_new_house(person,new_house):
    """Move an individual and their co-resident family to a new house.
    
    Parameters
    ----------
    person : Person
        A Person who will be moved along with their co-resident family.
    new_house : House
        The new house into which they will be moved.    
    
    Note
    ----
    This function assumes a patriline/male dominance of household. This needs to 
    be updated as part of the matrilineal update.
    """
    if person.has_house == new_house:
        pass #do nothing, already lives there!
    else:
        old_house = person.has_house
        #Get the coresident nuclear family
        family = kinship.get_family(person)
        family = [f for f in family if f in old_house.people]
        for member in family:
            if member.lifestatus == dead:
                pass
            else:
                old_house.remove_person(member)
                new_house.add_person(member)


def move_household_to_new_house(person,new_house):
    """Move an individual and their co-residential group to a new house.
    
    Parameters
    ----------
    person : Person
        A Person who will be moved along with their co-residential group.
    new_house : House
        The new house into which they will be moved.    
    
    Note
    ----
    This function assumes a patriline/male dominance of household. This needs to 
    be updated as part of the matrilineal update.
    """
    if person.has_house == new_house:
        pass #Nothing happens, person already lives there!
    else:
        old_house = person.has_house
        #Get the coresident household
        household = residency.get_household(old_house)
        for member in household:
            old_house.remove_person(member)
            new_house.add_person(member)

#old fragmentation functions to be removed in future
# def no_fragmentation(house):
#     """No fragmentation rule.
    
#     A household with this rule will never fragment.
    
#     Parameters
#     ---------
#     house : House
#         The household which won't fragment.
#     """
#     pass

# def brother_loses_out(house,age):
#     """Non-owner adult brothers leave when the oldest brother inherits the house. 
    
#     A (younger) adult brother who just lost out on the family inheritance leaves the
#     house along with his family. Otherwise, everyone stays put.
    
#     Parameters
#     ---------
#     house : House
#         The household to check to see if it will fragment.
#     age : int
#         The age of majority (marriage often) for determining whether an adult 
#         brother feels the pressure to leave and create a new household.
#     """
#     # Check whether any brothers are there
#     if house.people != [] and house.owner != None:    
#         siblings = kinship.get_siblings(house.owner)
#         if siblings != []:
#             siblings = [x for x in siblings if x.sex == male and x.age >= age and x.lifestatus == alive]
#             if len(siblings) > 0:
#                 for s in siblings:
#                     #For each brother who lives in the house
#                     if s in house.people:
#                         #If there is another brother over the age of majority who is
#                         ## not hte ownerwho lives there that person ( and their family)
#                         ## moves out
#                         # Pick a new house
#                         new_house = behavior.locality.get_empty_house(house.has_community.houses)
#                         if new_house != None:
#                             # Identify their family and move them
#                             behavior.mobility.move_family_to_new_house(s,new_house)
#                         else:
#                             # There is no new house, so stay put.
#                             pass               

# def house_gets_crowded(house):
#     """Over-capacity housing prompts families to relocate.
    
#     A house that exceeds its capacity gets rid of 1) non-kin of the owner,
#     2) more distant kin of the owner.
    
#     Parameters
#     ---------
#     house : House
#         The house to check for overcrowding.
#     """
#     pass #To be continued