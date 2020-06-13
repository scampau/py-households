"""Take machine-legible representations and make them human-legible

This module provide functionality for summarizing Person and House instances
that make them easier to read for a user of the households package.

This will eventually be extended to include Community and and World objects.
"""

from households import kinship, residency, main
from households.identity import *
#male, female = range(2)
print('loading narrative')

class Diary(object):
    """A place to record events as they occur for Persons.
    
    Parameters
    ----------
    associated
        The associated Person this is a diary of
    
    Attributes
    ----------
    events : dict
        A dict of Events by year.
    
    """
    def __init__(self,associated):
        if isinstance(associated, main.Person) == False and isinstance(associated, main.House) == False:
            raise TypeError('associated neither House nor Person')
        else:
            self.associated = associated
            self.events = {}
    
    @property
    def current_year(self):
        return self.associated.has_community.has_world.year
    
    def add_event(self,eventtype,detail = None):
        """Add an event to the Diary.
        
        Parameters
        ----------
        eventtype : Event Class
            An event that has occurred with its own particular class
        """
        if issubclass(eventtype,Event) == False:
            raise TypeError('event not of subclass Event')
        year = self.current_year
        if detail == None:
            event = eventtype(year,self.associated.has_house,self.associated)
        else:
            event = eventtype(year,self.associated.has_house,self.associated, detail)
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
    """The sort of circumstance recorded in a Diary.
    
    All events must take their inputs from __init__ and create a human-readable
    summary that includes the date as a formatted string
    """
    
    def __init__(self):
        pass
    
    # def summary(self):
    #     if len(self.__dict__.keys()) == 4: #transitive
    #         s = 'Year {}: {} ' + self.verb() + ' {}'
    #         return s.format(self.year, self.person, self.house)


#ALL OF THESE need a case for what happens when house is null
class BornEvent(Event):
    """When born
    
    """
    def __init__(self,year,house,person):
        self.year = year
        self.house = house
        self.person = person
    
    def summary(self):
        return 'Year {}: {} was born by {} at {}, {}'.format(self.year,self.person.name,self.mother.name,self.house.address,self.house.has_community.name)

class BirthEvent(Event):
    """Marks the birth of an individual
    
    """
    def __init__(self,year,house,person,child):
        self.year = year
        self.house = house
        self.person = person
        self.child = child

    def summary(self):
        return 'Year {}: {} gave birth to {} at {}, {}'.format(self.year,self.person.name,self.child.name,self.house.address,self.house.has_community.name)

class MarriageEvent(Event):
    """Marks the mariage of two people
    
    """
    def __init__(self,year,house,person,spouse):
        self.year = year
        self.house = house
        self.person = person
        self.spouse = spouse
    
    def summary(self):
        return 'Year {}: {} married {} at {}, {}'.format(self.year,self.person.name,self.spouse.name,self.house.address,self.house.has_community.name)

class MobilityEvent(Event):
    """Marks one person leaving a house for another
    
    """
    def __init__(self, year, house, person, oldhouse):
        self.year = year
        self.house = house
        self.person = person
        self.oldhouse = oldhouse
    
    def summary(self):
        return 'Year {}: {} moved from {}, {} to {}, {}'.format(self.year,self.person.name,self.oldhouse.address,self.oldhouse.has_community.name,self.house.address,self.house.has_community.name)

class DeathEvent(Event):
    def __init__(self,year,house,person):
        self.year = year
        self.house = house
        self.person = person
    
    def summary(self):
        return 'Year {}: {} died at {}, {}'.format(self.year,self.person.name,self.house.address,self.house.has_community.name)
    
class LeaveHouseEvent(Event):
    pass
    
    
class EnterhouseEvent(Event):
    pass

class ChangeOwnerEvent(Event):
    pass


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