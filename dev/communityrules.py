###############################################################################
#Several types of rules need to be easily changed.
## These include LOCALITY, INHERITANCE (who becomes the owner
### in the case of the death of the household patriarch), and FRAGMENTATION
### (WHen/how often do households split)

#Defining functions related to people according to their function.
#########################
# Locality functions (LOCALITY_MARRIAGE)

import numpy as np
import random as rd
import scipy as sp
import networkx as nx
import matplotlib.pyplot as plt
from kinship import *

global male, female
male, female = xrange(2)

def patrilocality(husband,wife):
    """
    Changes the house of the couple to that of the husband,
    If none or full, runs neolocality().
    
    husband, wife - the people just married
    
    """
    if husband.house == None:
        #The husband has no house; find a new one
        neolocality(husband,wife)
    elif len(husband.house.people)+1 >= husband.house.maxpeople:
        #If the house is full, find a new one and move out
        neolocality(husband,wife)
    else:
        #If the house has capacity, the wife moves in with the husband
        husband.house.add_person(wife)
        if wife.house is not None: wife.house.remove_person(wife)
        wife.house = husband.house
        

def neolocality(husband,wife,primary=male):
    """
    Finds a new house for a couple. Ownership is given to the primary sex.
    """
    #Select the primary person
    owner = husband if husband.sex == primary else wife
    # Find an empty house
    rd.shuffle(owner.comm.houses)
    foundone = False
    for h in owner.comm.houses:
        #If the house is empty and has no owner
        if len(h.people) == 0 and h.owner == None and foundone == False:
            # Add husband and wife to house
            h.people.extend([husband, wife])
            # Remove from their old houses
            if husband.house is not None:
                husband.house.people.remove(husband)
            if wife.house is not None:
                wife.house.people.remove(wife)
            # make whoever is of the primary sex the owner
            h.owner = owner
            # Add a pointed to the house from both individuals
            husband.house = h
            wife.house = h
            foundone = True
            break
    if foundone == False:
        print('No house found')
        pass #Future extension: if none found, couple may leave community

############
#Inheritance

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
    """
    old_house = agent.house
    family = get_family(agent,agent.comm.families)
    for member in family:
        if member.dead == True:
            pass
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
    children = get_children(agent,agent.comm.families)
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
    siblings = get_siblings(agent,agent.comm.families)
    
    if siblings != None:
        #If there are siblings, select the men
        select = [x for x in siblings if x.sex == male]
        if len(select) != 0:
            select.sort(reverse=True,key=lambda x:x.age)
            for brother in select:
                #Check whether each brother for sons
                children = get_children(brother,brother.comm.families)
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
    

## Inheritance regimes
### Each of these runs multiple rules
def inheritance_moderate(agent):
    """
    Upon the death of the patriarch, the house is given to someone in this
    order:
        
    Male children in order of age
    Children of brothers not in line for succession (have to move into household)
    
    This stems from the description of the moderate inheritance regime in Asheri
    """
    #The moderate inheritance regime of Asheri 1963
    # Check if patriarch
    if agent.sex == male and any([h.owner == agent for h in agent.comm.houses]):
        #First priority: male children
        inherited = inherit_sons(agent,True) #what about grandchildren?
        if inherited == False:
            #Second priority: adoption of brothers' younger sons
            inherited = inherit_brothers_sons(agent)
            if inherited == False:
                #If there is still no heir, for now the ownership defaults
                inherit(agent,None)                                  
    
    
    
def inheritance_radical():
    """
    Upon the death of the patriarch, the house is given to someone in this 
    order:
        
    Male children (partible!?)
    Brothers
    Children of brothers (stay where they are
    """
    