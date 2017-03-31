#########################
# Locality functions 

import numpy as np
import random as rd
import scipy as sp
import networkx as nx
import matplotlib.pyplot as plt

import kinship as kn

global male, female
male, female = xrange(2)

def get_empty_house(houses):
    """
    Get a randomly chosen empty house.
    """
    possible_houses = [h for h in houses if len(h.people) == 0 and h.owner == None]
    if len(possible_houses) == 0:
        ## if no houses available
        return None
    else:
        return rd.choice(possible_houses)
    

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
    new_house = get_empty_house(owner.comm.houses)
    if new_house == None:
        # If no house, end
        print('No house found')
        pass #Future extension: if none found, couple may leave community
    else:
        # Add husband and wife to house
        new_house.people.extend([husband, wife])
        # Remove from their old houses
        if husband.house is not None:
            husband.house.people.remove(husband)
        if wife.house is not None:
            wife.house.people.remove(wife)
        # make whoever is of the primary sex the owner
        new_house.owner = owner
        # Add a pointed to the house from both individuals
        husband.house = new_house
        wife.house = new_house
