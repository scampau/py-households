"""Take machine-legible representations and make them human-legible

This module provide functionality for summarizing Person and House instances
that make them easier to read for a user of the households package.

This will eventually be extended to include Community and and World objects.
"""

from households import kinship, residency
from households.identity import *
#male, female = range(2)
print('loading narrative')

class Diary(object):
    """A place to record events as they occur
    
    Parameters
    ----------
    associated
        The associated entity this is a diary of
    has_community : main.Community
        The associated community of this Diary
    
    
    Attributes
    ----------
    events : dict
        A dict of Events by year.
    
    """
    def __init__(self,associated,has_community):
        self.events = {}
        self.associated = associated
        if isinstance(has_community, main.Community) == False:
            raise TypeError('has_community not Community')
        else:
            self.has_community = has_community        
    
    def add_event(self,event):
        """Add an event to the Diary.
        
        Parameters
        ----------
        event : Event
            An event that has occurred with its own particular 
        """
        if isinstance(event,Event) == False:
            raise TypeError('event not Event')
        year = main.Community.year
        if year in self.events.keys():
            #This year already exists, so add to it
            self.events[year].append(event)
        else:
            #This year doesn't exist, so create it
            self.events[year] = [event]
            
    def get_events(self,year=None):
        """REturns the dict of all events or events from one year
        
        Parameters
        ----------
        year : None, int
            None if all years, int if one given year
            
        Returns
        -------
        dict of list of Events
            dict of Events, stored as lists of events with years as keys
        """
        if year is None:
            #REturn all events
            return self.events
        elif type(year) is int:
            #Return that year, if it exists
            if year in self.events.keys():
                return self.events[year]
            else:
                return []


class Event(object):
    """The sort of thing recorded in a Diary.
    
    All events must take their inputs from __init__ and create a human-readable
    summary that includes the date as a formatted string
    """
    
    def __init__(self):
        pass

    

class BirthEvent(Event):
    """Marks the birth of an individual
    
    """
    def __init__(self,year,mother,child,house):
        self.year = year
        self.mother = mother
        self.child = child
        self.house = house

    def summary(self):
        return 'Year {}: {} gave birth to {} at {}'.format(self.year,self.mother,self.child,self.house)

class MarriageEvent(Event):
    """Marks the mariage of two people
    
    """
    def __init__(self,year,husband,wife):
        self.year = year
        self.husband = husband
        self.wife = wife
    
    def suummary(self):
        return 'Year {}: {} married {}'.format(self.year,self.husband,self.wife)




###For biography and census of individual Person objects and House objects

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
    num_kids = len(kinship.get_children(person))
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
    if house.owner == None:
        text += ' with no owner'
    else:
        text += ' owned by ' + house.owner.name
    return text


male_names = ['Bernard','Arnold','Teddy','Lee','Hector','William','Robert','Logan','Lawrence','Peter']
female_names =  ['Dolores','Maeve','Armistice','Ashley','Theresa','Clementine','Elsie','Charlotte','Emily','Jasmyn']
address_names = ['Cactus Court','Tavern Trail','Main Street','Cattle Drive','Other Street','Mariposa Avenue']