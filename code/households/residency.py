"""Household classification functions based on residency and kinship.

This module implements definitions of household types, which relate residency
to kinship to define the coresident group based on relations. This
includes Laslett's 5-type typology as well as other definitions of households.

Most of the functions at present rely on the Cambridge Group typology for 
cross-cultural analysis, but are present in their most cited and thereby simplest
forms. A future expansion for this package would be to break these definitions 
into a subpackage of their own (e.g., residency.cambridge, residency.dukamakura,
etc.)

See also
--------
kinship
    The module that determines social relations regardless of residency.
        
"""
__all__ = ['count_married','get_married','is_solitary','is_no_family',
'is_nuclear','is_extended','is_multiple','classify_household','plot_classify',
'family_extract']

from households import np, rd, scipy, nx, plt, kinship
from households.identity import *
print('importing residency')

#global male, female
#male, female = range(2)
#"""Constants for refering to sex.
#"""

######Identify household/family types
# Using the Cambridge Group typology
def count_married(house):
    """Count the number of couples in a house.
    
    Parameters
    ----------
    house : House
        A house object to examine for coresident married couples.
        
    Returns
    -------
    int
        The number of coresident married couples.
    """
    if is_solitary(house):
        return 0
    m = 0
    for p in house.people:
        spouse = kinship.get_spouse(p,p.mycomm.families)
        if spouse is not None:
            if spouse in house.people:
                m += 1
    return m/2

def get_married(house):
    """Returns which persons are married in a household.
    
    Parameters
    ----------
    house : House
        A house object to examine for coresident married persons.
        
    Returns
    -------
    list of Person
        A list of the coresident married persons in a house.
    """
    if is_solitary(house):
        return []
    m = []
    for p in house.people:
        spouse = kinship.get_spouse(p,p.mycomm.families)
        if spouse is not None:
            if spouse in house.people:
                m.append(spouse)
    return m
    
def is_solitary(house):
    """Returns whether the household is occupied by a solitary individual.
    
    Parameters
    ----------
    house : House
        The house object to examine.
        
    Returns
    -------
    bool
        Whether the house is occupied by a single individual.
    """
    if len(house.people) == 1:
        return True
    return False

def is_no_family(house):
    """Returns whether the hosuehold is a 'no-family' type.
    
    Parameters
    ----------
    house : House
        The house object to examine.
        
    Returns
    -------
    bool
        Whether the house contains a 'no-family' type household.
    """
    #check whether there are any marriages
    m = count_married(house)
    if m == 0:
        return True
    else:
        return False    
                
def is_nuclear(house):
    """Returns whether the household is a single nuclear family w/o a prior generation.

    Parameters
    ----------
    house : House
        The house object to examine.
        
    Returns
    -------
    bool
        Whether the house contains a single nuclear family.
    """
    #One married coupls and no older generation from the owner
    #If the house has an owner
    m = count_married(house)
    if m == 1:
        #Check whether the married couple has parents there
        married = get_married(house)
        for p in married:
            parents = kinship.get_parents(p,p.mycomm.families)
            if parents is not None:
                for q in parents:
                    if q in house.people:
                        return False
        return True
    return False

    
def is_extended(house):
    """Returns whether the house is a single extended family.
    
    The extended family is defined as a nuclear family plus one member of an 
    older generation.
    
    Parameters
    ----------
    house : House
        The house object to examine.
        
    Returns
    -------
    bool
        Whether the house contains an extended family household.
    """
    #One married coupls and no older generation from the owner
    #If the house has an owner
    m = count_married(house)
    if m == 1:
        #Check whether the married couple has parents there
        married = get_married(house)
        for p in married:
            parents = kinship.get_parents(p,p.mycomm.families)
            if parents is not None:
                for q in parents:
                    if q in house.people:
                        return True
        return False
    return False
       
def is_multiple(house):
    """Whether the house is a multiple family household.
    
    The multiple family type is defined by the presence of two or more nuclear
    families cohabitating.
    
    Parameters
    ----------
    house : House
        The house object to examine.
        
    Returns
    -------
    bool
        Whether the house contains a multiple family household.
    """
    m = count_married(house)
    if m >= 2:
        return True
    return False
    
def classify(house):
    """Classify a given house into the Cambridge Group typology.
    
    Parameters
    ----------
    house : House
        The house object to examine.
        
    Returns
    -------
    {'empty','solitary','no-family','nuclear','extended','multiple'}
        Classification of the house into the Cambridge group typology
    """
    if house.people == []:
        return 'empty'
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
    """Classify houses at the present moment into their Cambridge Group typology
    
    Uses matplotlib.pyplot to create a bargraph of the current classification
    of households. Ignores empty houses (!).
    
    Parameters
    ----------
    houses : list of House
        A list of houses to classify, most easily a community.houses attribute. 
    """
    fig = plt.Figure()
    data = np.unique([classify(h) for h in houses if h.people != []],return_counts=True)
    order = [2,4,3,0,1]
    plt.bar(range(5),data[1][order]*1./sum(data[1]),width=.95)
    plt.xticks([i for i in range(5)],data[0][order])
    
    
#def family_extract(house):
#    """ACTIVE DEVELOPMENT: extract 
#    """
#    s = nx.subgraph(testcase.families,testcase.houses[0].people)
#    return s
#   ##THIS NEEDS WORK!!!
