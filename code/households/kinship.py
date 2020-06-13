"""Kinship functions for analyzing birth and marriage relationships.

This module uses the relationship network and a focal person to identify 
relationships such as spouses, children, parents, and nuclear families. By
providing a basic definition of children and parents in particular, it enables
more complex queries into cousins of varying degrees.

See also
--------
residency
    The module that analyzes kinship as it relates to residency, e.g. 
    co-residntial household structure.

"""
__all__ = ['get_spouse','get_parents','get_children','get_siblings',
'get_family']

#from households import np, rd, scipy, nx, plt
from households.identity import *
print('importing kinship')
#
#global male, female
#male, female = range(2)

def get_spouse(person):
    """Return the spouse of a person; otherwise return None.
    
    Parameters
    ----------
    person : Person
        The person in question.
    
    Returns
    -------
    Person or None
        Returns the spouse of the person, otherwise returns None.
    """
    return person.has_spouse
    
    
def get_parents(person):
    """Return the parents of an individual; otherwise return empty list.
    
    Parameters
    ----------
    person : Person
        The Person in question.
    
    Returns
    -------
        {[Person, Person], []}
            Returns a list with the parents of the person, otherwise returns empty list.
    """
    return person.has_parents.copy()


def get_children(person):
    """Return the children of an individual; otherwise return empty list.
    
    Parameters
    ----------
    person : Person
        The Person in question.
    
    Returns
    -------
        {[Person,], None}
            Returns a list with the children of the person, otherwise returns None.
    """
    
    return person.has_children.copy()   
    
    
def get_siblings(person):
    """Return the siblings of an individual; otherwise, return None.
    
    Parameters
    ----------
    person : Person
        The Person in question.
    
    Returns
    -------
        {[Person,], None}
            Returns a list with the siblings of the person, otherwise returns None.
    """
    
    parents = get_parents(person)
    if parents == []:
        return [];
    children = get_children(parents[0])
    children.remove(person)
    return children


def get_family(person):
    """Return a person's nuclear family (spouse and children) including themselves.
    
    Parameters
    ----------
    person : Person
        The Person in question.
    
    Returns
    -------
    [Person,]
        Returns a list with the nuclear family of the person,
        otherwise returns None.
    """
    spouse = get_spouse(person)
    if spouse == None:
        #If no spouse, then no children, so return self
        return [person]
    else:
        #If spouse, check for children
        children = get_children(person)
        return [person,spouse] + children    



