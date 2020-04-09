"""Kinship functions for analyzing birth and marriage relationships.

This module uses the relationship network and a focal agent to identify 
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

from households import np, rd, scipy, nx, plt

print('importing kinship')

global male, female
male, female = range(2)

def get_spouse(agent,network):
    """Return the spouse of an agent; otherwise return None.
    
    Parameters
    ----------
    agent : Person
        The person in question.
    network : networkx.DiGraph
        The social network which defines birth and marriage relations.
    
    Returns
    -------
        Person or None
            Returns the spouse of the agent, otherwise returns None.
    """
    inedges = network.in_edges(agent)
    if len(inedges) == 0:
        return None;
    else:
        for x, y in inedges:
            if network[x][y]['relation'] == 'marriage':
                return x;
        return None
    
    
def get_parents(agent,network):
    """Return the parents of an individual; otherwise return None.
    
    Parameters
    ----------
    agent : Person
        The Person in question.
    network : networkx.DiGraph
        The social network which defines birth and marriage relations.
    
    Returns
    -------
        {[Person, Person], None}
            Returns a list with the parents of the agent, otherwise returns None.
    """
    inedges = network.in_edges(agent)
    parents = []
    if len(inedges) == 0:
        return None;
    else:
        for x, y in inedges:
            if network[x][y]['relation'] == 'birth':
                parents.append(x)
    if len(parents) == 0:
        return None
    else:
        return parents


def get_children(agent,network):
    """Return the children of an individual; otherwise return None.
    
    Parameters
    ----------
    agent : Person
        The Person in question.
    network : networkx.DiGraph
        The social network which defines birth and marriage relations.
    
    Returns
    -------
        {[Person,], None}
            Returns a list with the children of the agent, otherwise returns None.
    """
    
    outedges = network.out_edges(agent)
    children = []
    if len(outedges) == 0:
        return None
    else:
        for x,y in outedges:
            if network[x][y]['relation']=='birth':
                children.append(y)
    if len(children) == 0:
        return None
    else:
        return children            
    
    
def get_siblings(agent,network):
    """Return the siblings of an individual; otherwise, return None.
    
    Parameters
    ----------
    agent : Person
        The Person in question.
    network : networkx.DiGraph
        The social network which defines birth and marriage relations.
    
    Returns
    -------
        {[Person,], None}
            Returns a list with the siblings of the agent, otherwise returns None.
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
    """Return an agents nuclear family (spouse and children) including themselves.
    
    Parameters
    ----------
    agent : Person
        The Person in question.
    network : networkx.DiGraph
        The social network which defines birth and marriage relations.
    
    Returns
    -------
        {[Person,], None}
            Returns a list with the nuclear family of the agent,
                otherwise returns None.
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



