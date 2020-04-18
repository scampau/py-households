"""Take machine-legible representations and make them human-legible

This module provide functionality for summarizing Person and House instances
that make them easier to read for a user of the households package.

This will eventually be extended to include Community and and World objects.
"""

from households import kinship, residency
from households.identity import *
#male, female = range(2)
print('loading narrative')

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

def biography(person):
    """Give a short, machine and human readable biography of a person
    
    Parameters
    ---------
    person : Person
        The person to return a biography of
    
    Returns:
    --------
    str
        str of life details
    """
    num_kids = len(kinship.get_children(person,person.mycomm.families))
    if person.marriagestatus == married or person.marriagestatus == widowed:
        if num_kids == 0:
            kids = 'no children'
        elif num_kids == 1:
            kids = 'one child'
        else:
            kids = '%i children'%(num_kids)
        marriage_summary = person.marriagestatus.adjective + ' with ' + kids
    else:
        marriage_summary = person.marriagestatus.adjective
    details = (person.name, person.lifestatus.adjective, person.sex.noun, age_to_text(person.age),marriage_summary )
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