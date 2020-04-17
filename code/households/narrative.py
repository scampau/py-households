"""Take machine-legible representations and make them human-legible

This module provide functionality for summarizing Person and House instances
that make them easier to read for a user of the households package.

This will eventually be extended to include Community and and World objects.
"""

from households import kinship, residency

def biography(person):
    """Give a short, machine and human readable biography of a person
    
    """
    return (person.dead, person.age, person.sex, person.married, len(households.kinship.get_children(person,person.mycomm.families)))

def census(house):
    """Returns the number of people and the Laslett classification of the household.
    
    """
    return (len(house.people),households.residency.classify(house))