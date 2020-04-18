"""Locality decisions for newlyweds.

The locality package encodes options for where a new couple live.


"""

from households import np, rd, scipy, nx, plt, kinship, residency
from households.identity import *
print('importing locality')
#import kinship as kn

#global male, female
#male, female = range(2)

def get_empty_house(houses):
    """Get a randomly chosen empty house to move into.
    
    Parameters
    ---------
    houses : list of House
        The Community.houses list for the community in question, or another 
        subset of houses.
    
    Returns
    -------
    None or House
        Picks an empty house if one exists, otherwise returns None.
    """
    possible_houses = [h for h in houses if len(h.people) == 0 and h.owner == None]
    if len(possible_houses) == 0:
        ## if no houses available
        return None
    else:
        return rd.choice(possible_houses)
    

def patrilocality(husband,wife):
    """Newlyweds live at the husband's family's house, or if no house find a new one.
    
    Changes the house of the couple to that of the husband,
    If none or full, runs neolocality().
    
    Parameters
    ----------
    husband, wife : Person
        The people just married, identified by sex.
    
    Returns
    -------
    bool
        True if patrilocality achieved, False if neolocality chosen instead.
    
    """
    if husband.has_house == None:
        #The husband has no house; find a new one
        neolocality(husband,wife,male)
        return False
    elif len(husband.has_house.people)+1 >= husband.has_house.maxpeople:
        #If the house is full, find a new one and move out
        neolocality(husband,wife,male)
        return False
    else:
        #If the house has capacity, the wife moves in with the husband
        husband.has_house.add_person(wife)
        if wife.has_house is not None: wife.has_house.remove_person(wife)
        wife.has_house = husband.has_house
        return True

def matrilocality(husband,wife):
    """Newlyweds live at the wife's family's house, or if no house find a new one.
    
    Changes the house of the couple to that of the wife,
    If none or full, runs neolocality().
    
    Parameters
    ----------
    husband, wife : Person
        The people just married, identified by sex.
    
    Returns
    -------
    bool
        True if matrilocality achieved, False if neolocality chosen instead.
    
    """
    if wife.has_house == None:
        #The husband has no house; find a new one
        neolocality(husband,wife,female)
        return False
    elif len(husband.has_house.people)+1 >= husband.has_house.maxpeople:
        #If the house is full, find a new one and move out
        neolocality(husband,wife,female)
        return False
    else:
        #If the house has capacity, the wife moves in with the husband
        wife.has_house.add_person(husband)
        if husband.has_house is not None: wife.has_house.remove_person(wife)
        husband.has_house = wife.has_house
        return True

def neolocality(husband,wife,primary):
    """Finds a new house for a couple. 
    
    Ownership is given to the primary sex.
    
    Parameters
    ----------
    husband, wife : Person
        The people just married, identified by sex.
    primary : Sex
        Defines the sex of the partner who formally owns the property.
    
    Returns
    -------
    bool
        If neolocality achieved, True; False otherwise.
    """
    #Select the primary person
    owner = husband if husband.sex == primary else wife
    # Find an empty house
    new_house = get_empty_house(owner.has_community.houses)
    if new_house == None:
        # If no house, end
        return False
        pass #Future extension: if none found, couple may leave community or build
    else:
        # Add husband and wife to house
        new_house.people.extend([husband, wife])
        # Remove from their old houses
        if husband.has_house is not None:
            husband.has_house.people.remove(husband)
        if wife.has_house is not None:
            wife.has_house.people.remove(wife)
        # make whoever is of the primary sex the owner
        new_house.owner = owner
        # Add a pointed to the house from both individuals
        husband.has_house = new_house
        wife.has_house = new_house
        return True
