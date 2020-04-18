"""Take machine-legible representations and make them human-legible

This module provide functionality for summarizing Person and House instances
that make them easier to read for a user of the households package.

This will eventually be extended to include Community and and World objects.
"""

from households import kinship, residency
from households.identity import *
#male, female = range(2)
print('loading narrative')

#def dead_to_text(dead):
#    """Takes a death and returns a string
#    
#    Parameters
#    ----------
#    dead : bool
#        Whether the person is dead
#        
#    Returns
#    -------
#    str
#    """
#    if type(dead) == bool:
#        if dead == True:
#            return 'dead'
#        else:
#            return 'living'
#    else:
#        raise TypeError('dead is not bool')
#
#def sex_to_text(sex):
#    """Takes a sex and returns a string
#    
#    Parameters
#    ----------
#    sex : {male, female}
#        The sex to be made into a string
#    
#    Returns
#    -------
#    str
#    """
#    if sex == male:
#        return 'male'
#    elif sex == female:
#        return 'female'
#    else:
#        raise ValueError('Sex neither male nor female')

def age_to_text(age):
    """Format age as a string
    
    Parameters
    ----------
    age : int
        The age to format
        
    Returns
    -------
    str
    """
    if type(age) == int:
        if age == 1:
            return '1 year old'
        else:
            return '%i years old'%(age)
    else:
        raise TypeError('age is not int')

#def married_to_text(married):
#    """Returns a string describing if the person is married
#    
#    Parameters
#    ----------
#    married : {bool,None}
#        The married status of a person
#    
#    Returns
#    -------
#    str
#    """
#    if type(married) == type(None):
#        return 'ineligible for marriage'
#    elif type(married) == bool:
#        if married == True:
#            return 'married'
#        else:
#            return 'eligible for marriage'        
#    else:
#        raise TypeError('married is not bool or NoneType')

def biography(person):
    """Give a short, machine and human readable biography of a person
    
    Parameters
    ---------
    person : Person
        The person to return a biography of
    
    Returns:
    str
        str of life details
    
    """
    num_kids = len(kinship.get_children(person,person.mycomm.families))
    if person.married == married or person.married == widowed:
        if num_kids == 0:
            kids = 'no children'
        elif num_kids == 1:
            kids = 'one child'
        else:
            kids = '%i children'%(num_kids)
        marriage_summary = person.married.adjective + ' with ' + kids
    else:
        marriage_summary = person.married.adjective
    details = (person.name, person.dead.adjective, person.sex.noun, age_to_text(person.age),marriage_summary )
    text = '%s is a %s %s, %s, %s' % details
    return text

def census(house):
    """Returns the number of people and the Laslett classification of the household.
    
    """
    details = (residency.classify(house), len(house.people))
    if details[1] == 1:
        text = 'a %s household with %i person residing' % details
    else:
        text = 'a %s household with %i people residing' % details
    return text


male_names = ['Bernard','Arnold','Teddy','Lee','Hector','William','Robert','Logan','Lawrence','Peter']
female_names =  ['Dolores','Maeve','Armistice','Ashley','Theresa','Clementine','Elsie','Charlotte','Emily','Jasmyn']