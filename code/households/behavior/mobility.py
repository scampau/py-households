"""Enable individuals and groups to move for reasons outside of direct life events.

These functions are run by indivudals each year to decide whether they/their family
needs to split apart into new households. This is to model conflicts such as
brother-brother conflicts after the death of the patriarch, as well as economic
mobility and military service.

Each mobility function will need to take a Person and determine 
whether they need to mvove. If they do, move them.

"""

from households import np, rd, scipy, nx, plt, inspect, kinship, residency, behavior, main
from households.identity import *

print('importing mobility')

class MobilityRule(behavior.Rule):
    """Define how and why people leave a household or a house.
    
    Mobility rules consist of a context for mobility, a way to identify
    who will leave, and a destination for them. They then move. The focal person
    is the new owner of the house.
    
    Parameters
    ----------
    check_household : callable
        Takes a person, returns True if it their house will fragment, False otherwise. Can 
        include randomness.
    who_leaves_house : callable
        Takes a person, returns who will leave their house. If no eligible to leave, return []
    destination : callable
        Takes a house and a group to move and identifies the house where they will move.
        The mobility rule does the relocation of people in who_leaves_house.
    
    """
    
    def __init__(self, check_household, who_leaves_house, destination):
        #make sure all are callable and take the right number of arguments
        for r, n in zip([check_household, who_leaves_house, destination],[1,1,2]):
            if self.__verify_callable__(r,[n]) == True:
                pass
            else:
                raise ValueError('wrong number of arguments for '+str(r.__name__))
        self.__check_household = check_household
        self.__who_leaves_house = who_leaves_house
        self.__destination = destination
    
    def __call__(self, person):
        """Determine if a person will cause their household to fragment, and carry it out if so.
        
        Parameters
        ----------
        house : main.House
            The house in question.
            
        Returns
        -------
        bool
            True if mobility/migration occurred, else False.
        
        """
        if self.__verify_person__(person) == False:
            raise TypeError('person not an instance of Person')
        #if it really is a house, then first identify whether it will fragment
        if person.has_house == None:
            return False #this person doesn't live in a house right now
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
                goto.owner = person #set the person as teh owner of the house
                for p in who_leaves:
                    move_person_to_new_house(p,goto)
                return True
        else:
            return False


class MobilityRuleMultiple(MobilityRule):
    """Chain multiple MobilityRules together; carried out in order.
    
    Currently unimplemented.
    """
    
    pass
    

#check household conditions
def check_household_overcrowded(person):
    """Return whether the household is overcrowded.
    
    Parameters
    ----------
    person : main.Person
        The person whose house to check.

    Returns
    -------
    bool
        True if the household is overcrowded, else False.

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
    """Return that the household doesn't fragment.
    
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

def check_household_younger_brothers_disinherited(person,age_of_majority):
    """Return whether the person is a younger disinherited brother of the owner.
    
    Parameters
    ----------
    person : main.Person
        The person whose house to check.
    age_of_majority : int
        The age of majority (marriage often) for determining whether an adult 
        brother feels the pressure to leave and create a new household.

    Returns
    -------
    bool
        Whether the household will fragment.

    """
    if isinstance(person,main.Person):
        house = person.has_house
        if house == None:
            return False #This person doesn't live in a house right now
        #If not the owner but a brother is and this person is eligible to 
        ##marry/own property/is above the age of majority:
        if house.owner != person and house.owner in kinship.get_siblings(house.owner) and person.age >= age_of_majority and person.sex == male:
            return True
        else:
            return False
    else:
        raise TypeError('person not Person')

#who_leaves
def who_leaves_house_non_kin(person):
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


def who_leaves_house_young_adult_brothers(person, age):
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


def who_leaves_house_noone(person):
    """Return that noone needs to leave."""
    if isinstance(person,main.Person):
        return []
    else:
        raise TypeError('person not Person')
        
def who_leaves_house_family(person):
    """Make the family of the focal person leave."""
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
    """Find a suitable house in the same village.

    Parameters
    ----------
    house : main.House
        The current House to be left.
    who_leaves : list of main.Person
        Who will be leaving.

    Returns
    -------
    house
        The new House to move to.

    """
    houses = who_leaves[0].has_community.houses
    possible_houses = [h for h in houses if len(h.people) == 0 and h.owner == None]
    if len(possible_houses) == 0:
        ## if no houses available
        return None
    else:
        return rd.choice(possible_houses)
    
def destination_radnom_house_random_village(house, who_leaves, weighting = "population"):
    """Pick a random house in a random other village.
    
    Unimplemented.

    Parameters
    ----------
    house : main.House
        The current House to be left.
    who_leaves : list of main.Person
        Who will be leaving.
    weighting : ['population','empty_houses','equal']
        What weighting to use for the random village selection

    Returns
    -------
    house

    """
    #Unimplemented.
    pass

def destination_random_house_specific_village(house, who_leaves, community):
    """Select a random house in a particular village (e.g. a destination community)

    Parameters
    ----------
    house : main.House
        The current House to be left.
    who_leaves : list of main.Person
        Who will be leaving.
    community : main.Community
        The new community to move to.

    Returns
    -------
    house
        The new house to move to.

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
