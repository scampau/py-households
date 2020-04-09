"""Determines how property is transmitted and where heirs live.

This module models inheritance as well as families moving as part of inheriting new property.
"""

from households import np, rd, scipy, nx, plt, kinship, residency

print('importing inheritance')
#import kinship as kn

global male, female
male, female = range(2)

#Basic inheritance functions
def inherit(dead,heir):
    """Once an heir is selected, move a dead person's house's/houses' ownership.
    
    Parameters
    ----------
    dead : Person
        The Person who has died and whose property needs to be moved
    heir : Person
        The Person who will inherit and will become the owner of the property.
    """
    for h in dead.mycomm.houses:
        if h.owner == dead:
            h.owner = heir

def move_family(agent,new_house):
    """Move an individual and their co-resident family to a new house.
    
    Parameters
    ----------
    agent : Person
        A Person who will be moved along with their co-resident family.
    new_house : House
        The new house into which they will be moved.    
    
    Note
    ----
    This function assumes a patriline/male dominance of household. This needs to 
    be updated as part of the matrilineal update.
    """
    old_house = agent.myhouse
    #Get the coresident family
    family = kinship.get_family(agent,agent.mycomm.families)
    family = [f for f in family if f in old_house.people]
    for member in family:
        if member.dead == True:
            pass
        else:
            if member.married == True and member.sex == male and member != agent:
                #If the person is married, move their family over as well 
                #families counted by husband so as not to duplicate
                move_family(member,new_house)
            else:
                old_house.remove_person(member)
                new_house.add_person(member)
                member.myhouse = new_house

#More complicated inheritance functions
## Each of these checks a subset of individuals and returns whether one of them
### inherited property
def inherit_sons(agent,checkowner=True):
    """The sons of an agent inherit. Returns True if inheritance took place.
    
    Parameters
    ----------
    agent : Person
        The Person whose property will be inherited.
    checkowner : bool, optional
        If True, do not let current owners inherit; if False, let them inherit any way.
    
    Returns
    -------
    bool
        True if inheritance took place.
    
    Notes
    -----
    Note that this includes an age bias towards the oldest;
    this needs to be a strategy/variable.
    
    This also includes an assumption that ownership is part of residency.
    """
    heir = None
    # Get a list of children
    children = kinship.get_children(agent,agent.mycomm.families)
    if children != []:
        #If there are children, select the men
        select = [x for x in children if x.sex == male and x.dead == False]
        #If there are alive men, select the oldest
        if len(select) != 0:
            select.sort(reverse=True,key=lambda x:x.age)
            for son in select:
                # If the son is not a house owner OR we don't care
                if son.myhouse.owner != son or checkowner == False :
                    #This works because if you inherit a house, you move into it
                    heir = son
                    if heir.myhouse != agent.myhouse:
                        move_family(heir,agent.myhouse)
                    inherit(agent,heir)
                    return True
    return False
    
#  inherit_brothers

def inherit_brothers_sons(agent,checkowner=True):
    """The sons of a man's brothers inherit. Returns true if successful.

    Parameters
    ----------
    agent : Person
        The Person whose property will be inherited.
    checkowner : bool, optional
        If True, do not let current owners inherit; if False, let them inherit any way.
    
    Returns
    -------
    bool
        True if inheritance took place.   
    """
    heir = None
    #Get a list of siblings
    siblings = kinship.get_siblings(agent,agent.mycomm.families)
    if siblings != []:
        #If there are siblings, select the men
        select = [x for x in siblings if x.sex == male]
        if len(select) != 0:
            select.sort(reverse=True,key=lambda x:x.age)
            for brother in select:
                #Check whether each brother for sons
                children = kinship.get_children(brother,brother.mycomm.families)
                if children != []:
                    #If the brother has children, check for the alive men
                    select = [x for x in children if x.sex == male and x.dead == False]
                    if checkowner == True:
                        select = [x for x in select if x.myhouse.owner != x]
                    if len(select) > 1:
                        # If there is more than one alive male child, then take 
                        ## the second oldest
                        select.sort(reverse=True,key=lambda x:x.age)
                        heir = select[1]
                        move_family(heir,agent.myhouse)
                        inherit(agent,heir)
                        return True
                    #Otherwise, not enough children
                # Otherwise, no children
            # Every brother has been checked
    return False
    
#def inherit_else_default ## A function to run inheritance functions and then
## stop if none work. Needs to run them sequentially in order