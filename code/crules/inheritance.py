############
#Inheritance

#import numpy as np
#import random as rd
#import scipy as sp
#import networkx as nx
#import matplotlib.pyplot as plt

import kinship as kn

global male, female
male, female = xrange(2)

#Basic inheritance functions
def inherit(dead,heir):
    """
    Once an heir is selected, move the house's/houses' ownership
    """
    for h in dead.comm.houses:
        if h.owner == dead:
            h.owner = heir

def move_family(agent,new_house):
    """
    Move an individual and their co-resident family to a new house.
    
    Note: this function assumes a patriline/male dominance of household.
    """
    old_house = agent.house
    #Get the coresident family
    family = kn.get_family(agent,agent.comm.families)
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
                member.house = new_house

#More complicated inheritance functions
## Each of these checks a subset of individuals and returns whether one of them
### inherited property
def inherit_sons(agent,checkowner=True):
    """
    The sons of an agent inherit. Returns True if inheritance took place
    """
    heir = None
    # Get a list of children
    children = kn.get_children(agent,agent.comm.families)
    if children != None:
        #If there are children, select the men
        select = [x for x in children if x.sex == male and x.dead == False]
        #If there are alive men, select the oldest
        if len(select) != 0:
            select.sort(reverse=True,key=lambda x:x.age)
            for son in select:
                # If the son is not a house owner OR we don't care
                if son.house.owner != son or checkowner == False :
                    #This works because if you inherit a house, you move into it
                    heir = son
                    if heir.house != agent.house:
                        move_family(heir,agent.house)
                    inherit(agent,heir)
                    return True
    return False
    
#  inherit_brothers

def inherit_brothers_sons(agent,checkowner=True):
    """
    The sons of a man's brothers inherit. Returns true if successful.
    """
    heir = None
    #Get a list of siblings
    siblings = kn.get_siblings(agent,agent.comm.families)
    
    if siblings != None:
        #If there are siblings, select the men
        select = [x for x in siblings if x.sex == male]
        if len(select) != 0:
            select.sort(reverse=True,key=lambda x:x.age)
            for brother in select:
                #Check whether each brother for sons
                children = kn.get_children(brother,brother.comm.families)
                if children != None:
                    #If the brother has children, check for the alive men
                    select = [x for x in children if x.sex == male and x.dead == False]
                    if checkowner == True:
                        select = [x for x in select if x.house.owner != x]
                    if len(select) > 1:
                        # If there is more than one alive male child, then take 
                        ## the second oldest
                        select.sort(reverse=True,key=lambda x:x.age)
                        heir = select[1]
                        move_family(heir,agent.house)
                        inherit(agent,heir)
                        return True
                    #Otherwise, not enough children
                # Otherwise, no children
            # Every brother has been checked
    return False
    
