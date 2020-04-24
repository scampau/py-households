"""Determines how property is transmitted and where heirs live.

This module models inheritance as well as families moving as part of inheriting new property.
"""

from households import np, rd, scipy, nx, plt, inspect, kinship, residency, main
from households.identity import *
print('importing inheritance')
#import kinship as kn

#Create a class that encompasses proper behavior for an inheritance rule
class InheritanceRule(object):
    """A class used for defining new inheritance rules.
    
    Inheritance is carried out upon the death of an individual by that
    individual. Thus an InheritanceRule as a callable can only take one argument.
    
    Parameters
    ---------
    has_property : callable
        Takes a Person. Returns True if the given person has property to give,
        else returns False.
    rule : callable
        A function that takes 1 argument (a person) and determines if they have
        property, how it will be inherited, and moves the property. It must return
        a bool of whether inheritance happened. The most generic form of an 
        InheritanceRule.
    failure : callable
        If inheritance fails, define what to do. Takes a Person, returns bool.
    """
    def __init__(self,has_property,rule,failure):
        #make sure all are callable and take the right number of arguments
        for r in [has_property,rule,failure]:
            if self.__verify_rule__(r,[1]) == True:
                pass
            else:
                raise ValueError('wrong number of arguments for '+str(r.__name__))
        self.__has_property = has_property
        self.__rule = rule
        self.__failure = failure
        
    def __call__(self,person):
        """Determines whether a person has property that needs to be inherited.
        
        Parameters
        ----------
        person : Person
            The Person who just died and who may need to have property divided.
        
        Returns
        -------
        bool
            Whether inheritance happened
        """
        if self.__verify_person__(person):
            if self.__has_property(person) == False:
                #no property, so no inheritance
                return False
            result = self.__rule(person)
            if type(result) == bool:
                if result == True:
                    return result
                else: #inheritance didn't happen for some reason
                    result = self.__failure(person)
                    if result == True:
                        return False
                    else:
                        raise ValueError('Something has gone horribly wrong')
            else:
                raise TypeError('returned result of rule is not bool')
    
    def __verify_rule__(self,rule,argnum = [1]):
        """Check that rule is callable and has only one non-default argument.
        
        Parameters
        ---------
        rule : callable
            A rule to check that it is callable and has the right number of arguments
        argnum : list of int
            A list of acceptable integer values for arguments passed to rule
            
        Returns
        ------
        bool
            True if properly formatted, False if not + raises an error
        """
        if callable(rule) == True:
            #Now count non-default arguments, must be 0 or 1
            sig = inspect.signature(rule)
            if sum([y.default == inspect._empty for y in sig.parameters.values()]) in argnum:
                return True
            else:
                raise ValueError(rule.__name__ + ' has the wrong number of non-default arguments')
                return False
        else:
            raise TypeError('rule is not callable')
            return False
        
    def __verify_person__(self,person):
        """Check that person is a Person
        """
        if isinstance(person,main.Person) == False:
            raise TypeError('person not an instance of Person')
            return False
        else:
            return True

#This can be used with some simple rules, like inherit_sons or inherit_brothers_sons
## Each of these checks a subset of individuals and returns a bool of whether one of them
### inherited property
def inherit_sons(person,checkowner=True):
    """The sons of a person inherit. Returns True if inheritance took place.
    
    Parameters
    ----------
    person : Person
        The Person whose property will be inherited.
    checkowner : bool, optional
        If True, do not let current owners inherit; if False, let them inherit any way.
    
    Returns
    -------
    bool
        True if inheritance took place.
    
    Notes
    -----
    Note that this includes an age bias towards the oldest;
    this needs to be a strategy/variable.
    
    This also includes an assumption that ownership is part of residency.
    """
    heir = None
    # Get a list of children
    children = kinship.get_children(person,person.has_community.families)
    if children != []:
        #If there are children, select the alive male children
        select = [x for x in children if x.sex == male and x.lifestatus == alive]
        #If there are alive men, select the oldest
        if len(select) != 0:
            select.sort(reverse=True,key=lambda x:x.age)
            for son in select:
                # If the son is not a house owner OR we don't care
                if son.has_house.owner != son or checkowner == False :
                    #This works because if you inherit a house, you move into it
                    heir = son
                    #If the son lives in a different house, move his household
                    move_household_to_new_house(heir,person.has_house)
                    for h in person.has_community.houses:
                        if h.owner == person:
                            h.owner = heir
                    return True
                else:
                    pass #Try the next one
    return False
    
def inherit_brothers_sons(person,checkowner=True):
    """The sons of a man's brothers inherit. Returns true if successful.
    
    The second oldest son inherits, not the oldest, so that the oldest
    can inherit the brother's property.
    
    Parameters
    ----------
    person : Person
        The Person whose property will be inherited.
    checkowner : bool, optional
        If True, do not let current owners inherit; if False, let them inherit any way.
    
    Returns
    -------
    bool
        True if inheritance took place.   
    """
    heir = None
    #Get a list of siblings
    siblings = kinship.get_siblings(person,person.has_community.families)
    if siblings != []:
        #If there are siblings, select the men
        select = [x for x in siblings if x.sex == male]
        if len(select) != 0:
            select.sort(reverse=True,key=lambda x:x.age)
            for brother in select:
                #Check whether each brother for sons
                children = kinship.get_children(brother,brother.has_community.families)
                if children != []:
                    #If the brother has children, check for the alive male children
                    select = [x for x in children if x.sex == male and x.lifestatus == alive]
                    if checkowner == True:
                        select = [x for x in select if x.has_house.owner != x]
                    if len(select) > 1:
                        # If there is more than one alive male child, then take 
                        ## the second oldest (first must stay for brother's inheritance)
                        select.sort(reverse=True,key=lambda x:x.age)
                        heir = select[1]
                        move_family_to_new_house(heir,person.has_house)
                        for h in person.has_community.houses:
                            if h.owner == person:
                                h.owner = heir
                        return True
                    #Otherwise, not enough children
                # Otherwise, no children
            # Every brother has been checked
    return False
    
def inherit_sons_then_brothers_sons(person,checkowner=True) :
    """The sons of a Person and then the sons of his brothers inherit. Returns true if successful.
    
    Children inherit by age, oldest to youngest. For brothers, the second 
    oldest son inherits, not the oldest, so that the oldest can inherit
    the brother's property.
    
    Parameters
    ----------
    person : Person
        The Person whose property will be inherited.
    checkowner : bool, optional
        If True, do not let current owners inherit; if False, let them inherit any way.
    
    Returns
    -------
    bool
        True if inheritance took place.   
    """
    result = inherit_sons(person,checkowner)
    if result == False:
        result = inherit_brothers_sons(person,checkowner)
    return result
    
    
    
#More complex rules can also be created, however.
#In that case, use the InheritanceRuleComplex class to construct a sequenced rule    
class InheritanceRuleComplex(InheritanceRule):
    """A class used for defining complex or multistage inheritance rules.
    
    This function must assess whehter this person has property (houses) using
    a qualification (a function that returns true/false). If this person has property,
    then their heirs will be identified (using find_heirs). Heirs must be returned ranked,
    either as a list of person objects for single inheritance or as a list of lists of persons
    for multiple inheritance .Heirs will then be excluded based on limitations.
    Property is divided if it must be. 
    
    Parameters
    ----------
    has_property : callable
        Takes a Person. Returns True if the given person has property to give,
        else returns False.
    find_heirs : callable
        Takes a Person. Returns a list of heirs, ranked in order, either as a 
        list of Persons (single inheritance) or a list of lists of Persons 
        (multiple inheritance).
    limit_heirs : callable
        Takes a list of heirs, or a list of lists of heirs. Determines 
        eligibility to inherit of each Person. Removes all those who can't.
        Returns a modified list.
    distribute_property : callable
        Takes the person whose property is to be divided, as well as 
        a list of persons (or a list of lists of persons) and selects the 
        first person or group. Distributes the property among the group or 
        gives it all to one person. Returns True if this took place, False otherwise. 
    failure : callable
        If inheritance fails, define what to do. Takes a Person, returns bool.
    """
    
    def __init__(self,has_property,find_heirs,limit_heirs,distribute_property,failure):
        #make sure rule is callable
        for rule, argnum in zip([has_property,find_heirs,limit_heirs,distribute_property,failure],[[1],[1],[1],[2],[1]]):
            if self.__verify_rule__(rule,argnum) == True:
                pass
            else:
                raise ValueError('wrong number of arguments for '+str(rule.__name__))
        self.__has_property = has_property
        self.__find_heirs = find_heirs
        self.__limit_heirs = limit_heirs
        self.__distribute_property = distribute_property
        self.__failure = failure
        
    def __call__(self,person):
        """Determines whether a person has property that needs to be inherited.
        
        Parameters
        ----------
        person : Person
            The Person who just died and who may need to have property divided.
        
        Returns
        -------
        bool
            Whether inheritance happened
        """
        if self.__verify_person__(person) == False:
            raise TypeError('person not a Person')
        if self.__has_property(person) == True:
            #There is something to inherit
            #find the heirs
            heirs = self.__find_heirs(person) 
            if heirs == []:
                #No heirs, return False
                return False
            elif all([x == [] for x in heirs]):
                #No heirs in complex form, return False
                return False
            else:
                #remove any heirs who lack a qualification
                heirs = self.__limit_heirs(heirs) 
                #if there are any qualified heirs left, distribute the property
                if len(heirs) != 0:
                    #Run the distribution algorithm
                    outcome = self.__distribute_property(person,heirs)
                    return outcome
                else:
                    outcome = self.__failure(person)
                    if outcome == True:
                        return False                   
                    else:
                        raise ValueError('Something has gone horribly wrong')
        else:
            return False #nothing to inherit



#Basic inheritance functions for building inheritance rules
#Has property checks
def has_property_houses(person):
    """Check whether a person owns a house or houses
    
    Parameters:
    -----------
    person : Person
        Who to check for property
    """
    if isinstance(person,main.Person):
        for h in person.has_community.houses:
            if h.owner == person:
                return True
        return False
    else:
        raise TypeError('person not Person')
    
#Functions for finding heirs based on kinship

## Each of these checks a subset of individuals and returns whether one of them
### inherited property
def find_heirs_children_oldest_to_youngest(person,sex = None):
    """Returns the children of a person as a list
    
    Parameters
    ----------
    person : Person
        The Person whose property will be inherited.
    sex : identity.Sex or None
        If Sex, only return children of that sex; if None return either
        
    Returns
    -------
    list of Person
        The children of a person
    
    Notes
    -----
    Note that this includes an age bias towards the oldest;
    this needs to be a strategy/variable.
    
    This also includes an assumption that ownership is part of residency.
    """
    if isinstance(person,main.Person) == False:
        raise TypeError('person not Person')
    if isinstance(sex, Sex) == False and sex != None:
        raise TypeError('sex neither Sex nor None')
    # Get a list of children
    children = kinship.get_children(person,person.has_community.families)
    if children != []:
        #If there are children, select the living children
        if sex == None:
            select = [x for x in children if x.lifestatus == alive]
        else:
            [x for x in children if x.sex == sex and x.lifestatus == alive]
        select.sort(reverse=True,key=lambda x:x.age)
        return select
    return [] #no heirs, return empty list



def find_heirs_sons_oldest_to_youngest(person):
    """Returns the sons of a person as a list
    
    Parameters
    ----------
    person : Person
        The Person whose property will be inherited.
    
    Returns
    -------
    list of Person
        The sons of a person
    
    Notes
    -----
    Note that this includes an age bias towards the oldest;
    this needs to be a strategy/variable.
    
    This also includes an assumption that ownership is part of residency.
    """
    select = find_heirs_children_oldest_to_youngest(person,sex = male)
    return select

def find_heirs_daughters_oldest_to_youngest(person):
    """Returns the daughters of a person as a list
    
    Parameters
    ----------
    person : Person
        The Person whose property will be inherited.
    
    Returns
    -------
    list of Person
        The daughters of a person
    
    Notes
    -----
    Note that this includes an age bias towards the oldest;
    this needs to be a strategy/variable.
    
    This also includes an assumption that ownership is part of residency.
    """
    select = find_heirs_children_oldest_to_youngest(person,sex = female)
    return select
    
def find_heirs_brothers_sons_oldest_to_youngest(person,checkowner=True):
    """The sons of a man's brothers inherit, ranked by age.
    
    The ranking is both by brothers

    Parameters
    ----------
    person : Person
        The Person whose property will be inherited.
    
    Returns
    -------
    list of list of Person
        The sons of a Person's brother, grouped by brother, all sorted by age
    """
    #Get a list of siblings
    heirs = []
    siblings = kinship.get_siblings(person,person.has_community.families)
    if siblings != []:
        #If there are siblings, select the brothers
        select_brothers = [x for x in siblings if x.sex == male]
        if len(select_brothers) != 0:
            #If there are brothers, rank by age and select their chidlren
            select_brothers.sort(reverse=True,key=lambda x:x.age)
            for brother in select_brothers:
                #Check whether each brother for sons
                children = kinship.get_children(brother,brother.has_community.families)
                if children != []:
                    #If the brother has children, check for the alive male children
                    select = [x for x in children if x.sex == male and x.lifestatus == alive]
                    select.sort(reverse=True,key=lambda x:x.age)
                    heirs.append(select)
                else:
                    pass # Otherwise, no children
            # Every brother has been checked
    return heirs


#Limitation of heirs
def limit_heirs_none(heirs):
    """No limits on heirs.
    
    Parameter
    --------
    heirs : list of Person or list of list of Person
        heirs, the return argument of find_heirs type functions
    
    Returns
    -------
    heirs : list of Person or list of list of Person
        returns heirs, unmodified
    """
    return heirs

def limit_heirs_not_owners(heirs):
    """Heirs can't already own a house (limit one (1)).
    
    Parameter
    --------
    heirs : list of Person or list of list of Person
        heirs, the return argument of find_heirs type functions
    
    Returns
    -------
    new_heirs : list of Person or list of list of Person
        returns heirs with Persons who own property removed
    """
    new_heirs = []
    if isinstance(heirs[0],main.Person):
        #This a list of people, so go through each one and assess
        for p in heirs:
            if has_property_houses(p) == True:
                #Exclude this one
                pass
            else:
                new_heirs.append(p)
    elif type(heirs[0]) == list:
        #This is a list of lists of people, so go through each and assess
        if isinstance(heirs[0][0],main.Person) == False:
            raise TypeError('heirs neither list of Persons or list of lists of Person')
        for l in heirs:
            new_sublist = []
            for p in l:
                if has_property_houses(p) == True:
                    #Exclude this one
                    pass
                else:
                    new_sublist.append(p)
            if new_sublist != []:
                #IF any qualify, add back to new_heirs
                new_heirs.append(new_sublist)
    else:
        raise TypeError('heirs neither list of Persons or list of lists of Person')
    return new_heirs

def limit_heirs_by_age(heirs,age_of_majority = 15):
    """Heirs can't be below a given age of majority
    
    Parameter
    --------
    heirs : list of Person or list of list of Person
        heirs, the return argument of find_heirs type functions
    age_of_majority : int
        age heirs must be to qualify for inheritance
    
    Returns
    -------
    new_heirs : list of Person or list of list of Person
        returns heirs with Persons who own property removed
    """
    new_heirs = []
    if isinstance(heirs[0],main.Person):
        #This a list of people, so go through each one and assess
        for p in heirs:
            if p.age < age_of_majority == True:
                #Exclude this one
                pass
            else:
                new_heirs.append(p)
    elif type(heirs[0]) == list:
        if isinstance(heirs[0][0],main.Person) == False:
            raise TypeError('heirs neither list of Persons or list of lists of Person')
        #This is a list of lists of people, so go through each and assess
        for l in heirs:
            new_sublist = []
            for p in l:
                if p.age < age_of_majority == True:
                    #Exclude this one
                    pass
                else:
                    new_sublist.append(p)
            if new_sublist != []:
                #IF any qualify, add back to new_heirs
                new_heirs.append(new_sublist)
    else:
        raise TypeError('heirs neither list of Persons or list of lists of Person')
    return new_heirs

#Distribution of property and moving families/households
def distribute_property_to_first_heir_and_move_household(person,heirs):
    """Select first heir, move a dead person's house's/houses' ownership.
    Then move that person's household into the inherited house
    
    Parameters
    ----------
    person : Person
        The Person who has died and whose property needs to be moved
    heirs : list of Person, list of lists of Person, or Person
        The Person(s) who will inherit and will become the owner of the property.
        
    return
    ------
    bool
        Whether property transfer happened.
    """
    #Find the first heir and transfer their property
    if type(heirs) == list:
        heir = heirs[0]
        if isinstance(heir, main.Person):
            pass
        elif type(heir) == list:
            heir = heir[0]
            if isinstance(heir, main.Person) == False:
                raise TypeError('heirs neither Person nor list of Persons')
    elif isinstance(heirs,main.Person):
        heir = heirs
    else:
        raise TypeError('heirs neither Person nor list of Persons')
    #Now that the heir has been identified, transfer any property to their name
    transfer_happened = False
    for h in person.has_community.houses:
        if h.owner == person:
            h.owner = heir
            old_house = heir.has_house
            move_household_to_new_house(heir,h)
            transfer_happened = True
    return transfer_happened
    

def move_family_to_new_house(person,new_house):
    """Move an individual and their co-resident family to a new house.
    
    Parameters
    ----------
    person : Person
        A Person who will be moved along with their co-resident family.
    new_house : House
        The new house into which they will be moved.    
    
    Note
    ----
    This function assumes a patriline/male dominance of household. This needs to 
    be updated as part of the matrilineal update.
    """
    if person.has_house == new_house:
        pass #do nothing, already lives there!
    else:
        old_house = person.has_house
        #Get the coresident nuclear family
        family = kinship.get_family(person,person.has_community.families)
        family = [f for f in family if f in old_house.people]
        for member in family:
            if member.lifestatus == dead:
                pass
            else:
                old_house.remove_person(member)
                new_house.add_person(member)


def move_household_to_new_house(person,new_house):
    """Move an individual and their co-residential group to a new house.
    
    Parameters
    ----------
    person : Person
        A Person who will be moved along with their co-residential group.
    new_house : House
        The new house into which they will be moved.    
    
    Note
    ----
    This function assumes a patriline/male dominance of household. This needs to 
    be updated as part of the matrilineal update.
    """
    if person.has_house == new_house:
        pass #Nothing happens, person already lives there!
    else:
        old_house = person.has_house
        #Get the coresident household
        household = residency.get_household(old_house)
        for member in household:
            old_house.remove_person(member)
            new_house.add_person(member)

#What happens if inheritance fails?
def failed_inheritance_no_owner(person):
    """IF no one inherits, then the property defaults to no owner.
    
    Parameters
    ----------
    person : Person
        The person whose property must be changed to none
    
    Returns:
    --------
    bool
        Successful?
    """
    if isinstance(person,main.Person) == False:
        raise TypeError('person not a Person')
    transfer_happened = False
    for h in person.has_community.houses:
        if h.owner == person:
            h.owner = None
            transfer_happened = True
    return transfer_happened