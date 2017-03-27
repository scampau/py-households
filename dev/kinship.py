###################3
# Kinship functions
import numpy as np
import random as rd
import scipy as sp
import networkx as nx
import matplotlib.pyplot as plt

global male, female
male, female = xrange(2)

def get_spouse(agent,network):
    """
    Return the spouse of an agent; otherwise return None."
    """
    inedges = network.in_edges(agent)
    if len(inedges) == 0:
        return None;
    else:
        for x, y in inedges:
            if network[x][y]['type'] == 'marriage':
                return x;
        return None
    
    
def get_parents(agent,network):
    """
    Return the parents of an individual; otherwise return None.
    """
    inedges = network.in_edges(agent)
    parents = []
    if len(inedges) == 0:
        return None;
    else:
        for x, y in inedges:
            if network[x][y]['type'] == 'birth':
                parents.append(x)
    if len(parents) == 0:
        return None
    else:
        return parents


def get_children(agent,network):
    """
    Return the children of an individual; otherwise return None.
    """
    outedges = network.edge[agent]
    children = []
    if len(outedges) == 0:
        return None
    else:
        for y in outedges.iterkeys():
            if outedges[y]['type']=='birth':
                children.append(y)
    if len(children) == 0:
        return None
    else:
        return children            
    
    
def get_siblings(agent,network):
    """
    Return the siblings of an individual; otherwise, return None.
    """
    parents = get_parents(agent,network)
    if parents == None:
        return None;
    children = get_children(parents[0],network)
    children.remove(agent)
    if len(children) == 0:
        return None
    else:
        return children


def get_family(agent,network):
    """
    Return an agents nuclear family (spouse and children) including themselves.
    """
    spouse = get_spouse(agent,network)
    if spouse == None:
        #If no spouse, then no children, so return self
        return [agent]
    else:
        #If spouse, check for children
        children = get_children(agent,network)
        if children == None:
            return [agent,spouse]
        else:
            return [agent,spouse] + children    


######Identify household/family types
# Using the Cambridge Group typology
def count_married(house):
    """
    Count the number of couples in a house.
    """
    if is_solitary(house):
        return 0
    m = 0
    for p in house.people:
        spouse = get_spouse(p,p.comm.families)
        if spouse is not None:
            if spouse in house.people:
                m += 1
    return m/2

def get_married(house):
    """
    Returns the married agents in a household.
    """
    if is_solitary(house):
        return []
    m = []
    for p in house.people:
        spouse = get_spouse(p,p.comm.families)
        if spouse is not None:
            if spouse in house.people:
                m.append(spouse)
    return m
    
def is_solitary(house):
    """
    Returns whether the household is a solitary individual.
    """
    if len(house.people) == 1:
        return True
    return False

def is_no_family(house):
    """
    Returns whether the household is not a family, namely it has no marriages.
    """
    #check whether there are any marriages
    m = count_married(house)
    if m == 0:
        return True
    else:
        return False    
                
def is_nuclear(house):
    """
    Returns whether the household is a single nuclear family w/o a prior generation.
    """
    #One married coupls and no older generation from the owner
    #If the house has an owner
    m = count_married(house)
    if m == 1:
        #Check whether the married couple has parents there
        married = get_married(house)
        for p in married:
            parents = get_parents(p,p.comm.families)
            if parents is not None:
                for q in parents:
                    if q in house.people:
                        return False
        return True
    return False

    
def is_extended(house):
    #Returns whether the house is a single extended family
    #One married coupls and no older generation from the owner
    #If the house has an owner
    m = count_married(house)
    if m == 1:
        #Check whether the married couple has parents there
        married = get_married(house)
        for p in married:
            parents = get_parents(p,p.comm.families)
            if parents is not None:
                for q in parents:
                    if q in house.people:
                        return True
        return False
    return False
       
def is_multiple(house):
    m = count_married(house)
    if m >= 2:
        return True
    return False
    
def classify_household(house):
    if is_solitary(house):
        return 'solitary'
    elif is_no_family(house):
        return 'no-family'
    elif is_nuclear(house):
        return 'nuclear'
    elif is_extended(house):
        return 'extended'
    elif is_multiple(house):
        return 'multiple'
    else:
        return None

        
def plot_classify(houses):
    fig = plt.Figure()
    data = np.unique([classify_household(h) for h in houses if h.people != []],return_counts=True)
    order = [2,4,3,0,1]
    plt.bar(range(5),data[1][order]*1./sum(data[1]),width=.95)
    plt.xticks([i for i in range(5)],data[0][order])
    
    
def family_extract(house):
    s = nx.subgraph(testcase.families,testcase.houses[0].people)
    return s
[(i.age,i.sex) for i in testcase.houses[0].people if i.married != True]