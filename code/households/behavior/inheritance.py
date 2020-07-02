"""Determines how property is transmitted and where heirs live.

This module models defines the events that occur when a Person dies. While 
different types of InheritanceRules can be defined, most will use a combination
of functions (defined here and custom) to determine whether there is property 
that can be inherited, determine the heirs of that property, and enact any 
required residency changes.

The foundational InheritanceRule accomplishes this through three functions,
while the more advanced InheritanceRuleComplex accomplishes this with five.
The customizability of the latter is useful for articulating exactly how
Houses should be transmitted and occupied. 

A planned expansion is to have inheritance rules closely tied to (and likely 
containing) the AgeTable for dying, such that populations with different
mortality rates can be associated easily with different inheritance regimes.
"""

from households import np, rd, scipy, nx, plt, inspect, kinship, residency, main, behavior
from households.identity import *
print('importing inheritance')
#import kinship as kn

#Create a class that encompasses proper behavior for an inheritance rule
class InheritanceRule(behavior.Rule):
    """Define inheritance of property after death.
    
    Inheritance is carried out upon the death of an individual by that
    individual. Thus an InheritanceRule as a callable can only take one argument,
    the person who died. In doing so, it will call three other functions:
        1. has_property, to determine whether the individual has transmissable
            property;
        2. rule, which both carries out the property transmission and moves the
            ownership of the property as well as any people;
        3. failure, which is called only if an heir cannot be found or an 
            inheritance cannot be negotiated (or fails for other reasons.)
    
    Complications do not need to use this tripartite structure, but must be defined
    as subclasses in order to be recognized by the simulation as an inheritance
    rule.
    
    Built in rules compatible with step 2, `rule`, are prefixed with `simple_`
    in the module.
    
    Parameters
    ----------
    has_property : callable
        Takes a Person. Returns True if the given person has property to give,
        else returns False.
    rule : callable
        A function that takes 1 argument (a person) and determines
        how property will be inherited, and moves the property. It must return
        a bool of whether inheritance happened. The most generic form of an 
        InheritanceRule.
    failure : callable
        If inheritance fails, define what to do. Takes a Person, returns bool.
    """
    #rule needs to be changed to a different variabule name (not an instance of Rule)
    def __init__(self,has_property,rule,failure):
        #make sure all are callable and take the right number of arguments
        for r in [has_property,rule,failure]:
            if self.__verify_callable__(r,1) == True:
                pass
            else:
                raise ValueError('wrong number of arguments for '+str(r.__name__))
        self.__has_property = has_property
        self.__rule = rule
        self.__failure = failure
        
    def __call__(self,person):
        """Determine whether inheritance happens and enact it.
        
        Called on a person when they die. Checks for property, subjects it to
        inheritance if needed, and either succeeds or follows through with 
        another routine if a failure.
        
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

#This can be used with some simple rules, like inherit_sons or inherit_brothers_sons
## Each of these checks a subset of individuals and returns a bool of whether one of them
### inherited property
def simple_inherit_sons(person,checkowner=True):
    """Give property to the sons of a person.
    
    Parameters
    ----------
    person : Person
        The Person whose property will be inherited.
    checkowner : bool, optional
        If True, do not let current owners inherit; if False, let them inherit any way.
    
    Returns
    -------
    bool
        True if inheritance took place, False otherwise.
    
    Notes
    -----
    Note that this includes an age bias towards the oldest;
    this needs to be a strategy/variable.
    
    This also includes an assumption that ownership is part of residency.
    """
    heir = None
    # Get a list of children
    children = kinship.get_children(person)
    if children != []:
        #If there are children, select the alive male children
        select = [x for x in children if x.sex == male and x.lifestatus == alive]
        #If there are alive men, select the oldest
        if len(select) != 0:
            select.sort(reverse=True,key=lambda x:x.age)
            for son in select:
                # If the son is an owner of the house he lives in OR we don't care
                if son not in son.has_house.get_owners() or checkowner == False :
                    #This works because if you inherit a house, you move into it
                    heir = son
                    #If the son lives in a different house, move his household
                    behavior.mobility.move_household_to_new_house(heir,person.has_house)
                    for h in person.has_community.has_world.houses:
                        if person in h.get_owners():
                            h.change_owner(person,heir)
                    return True
                else:
                    pass #Try the next one
    return False
    
def simple_inherit_brothers_sons(person,checkowner=True):
    """Give property to the second oldest son of a brother, ranked by age.
    
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
    siblings = kinship.get_siblings(person)
    if siblings != []:
        #If there are siblings, select the men
        select = [x for x in siblings if x.sex == male]
        if len(select) != 0:
            select.sort(reverse=True,key=lambda x:x.age)
            for brother in select:
                #Check whether each brother for sons
                children = kinship.get_children(brother)
                if children != []:
                    #If the brother has children, check for the alive male children
                    select = [x for x in children if x.sex == male and x.lifestatus == alive]
                    if checkowner == True:
                        select = [x for x in select if x not in x.has_house.get_owners()]
                    if len(select) > 1:
                        # If there is more than one alive male child, then take 
                        ## the second oldest (first must stay for brother's inheritance)
                        select.sort(reverse=True,key=lambda x:x.age)
                        heir = select[1]
                        behavior.mobility.move_family_to_new_house(heir,person.has_house)
                        for h in person.has_community.has_world.houses:
                            if person in h.get_owners():
                                h.change_owner(person, heir)
                        return True
                    #Otherwise, not enough children
                # Otherwise, no children
            # Every brother has been checked
    return False
    
def simple_inherit_sons_then_brothers_sons(person,checkowner=True) :
    """Give property to sons and then brothers' second sons.
    
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
    result = simple_inherit_sons(person,checkowner)
    if result == False:
        result = simple_inherit_brothers_sons(person,checkowner)
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
    
    Functions within the inheritance package are named with a prefix that 
    matches the parameter which they can fill.
    
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
        for rule, argnum in zip([has_property,find_heirs,limit_heirs,distribute_property,failure],[1,1,1,2,1]):
            if self.__verify_callable__(rule,argnum) == True:
                pass
            else:
                raise ValueError('wrong number of arguments for '+str(rule.__name__))
        self.__has_property = has_property
        self.__find_heirs = find_heirs
        self.__limit_heirs = limit_heirs
        self.__distribute_property = distribute_property
        self.__failure = failure
        
    def __call__(self,person):
        """Enact inheritance on a person's property, if they have any.
        
        Checks a person's property qualification, finds heirs, removes
        Persons who can't inherit for the given reasons, distributes the property,
        and otherwise enacts a protocol for a failed inheritance.
        
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
    """Check whether a person owns a house or houses.
    
    Parameters
    ----------
    person : Person
        Who to check for property
    """
    if isinstance(person,main.Person):
        for h in person.has_community.has_world.houses:
            if person in h.get_owners():
                return True
        return False
    else:
        raise TypeError('person not Person')
    
#Functions for finding heirs based on kinship

## Each of these checks a subset of individuals and returns whether one of them
### inherited property
def find_heirs_children_oldest_to_youngest(person,sex = None):
    """Return the children of a person as a list.
    
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
    children = kinship.get_children(person)
    if children != []:
        #If there are children, select the living children
        if sex == None:
            select = [x for x in children if x.lifestatus == alive]
        else:
            select = [x for x in children if x.sex == sex and x.lifestatus == alive]
        select.sort(reverse=True,key=lambda x:x.age)
        return select
    return [] #no heirs, return empty list

def find_heirs_sons_oldest_to_youngest(person):
    """Return the sons of a person as a list.
    
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
    """Return the daughters of a person as a list.
    
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

def find_heirs_siblings_children_oldest_to_youngest(person, sex = None):
    """Return the children of a Person's siblings, ranked by age.
    
    The ranking is both by brothers

    Parameters
    ----------
    person : Person
        The Person whose property will be inherited.
    sex : identity.Sex or None
        If Sex, only return children of that sex; if None return either
    
    Returns
    -------
    list of list of Person
        The sons of a Person's brother, grouped by brother, all sorted by age
    """
    # Type check
    if isinstance(person,main.Person) == False:
        raise TypeError('person not Person')
    if isinstance(sex, Sex) == False and sex != None:
        raise TypeError('sex neither Sex nor None')
    heirs = []
    #Get a list of siblings
    siblings = kinship.get_siblings(person)
    if siblings != []:
        #If there are siblings, do sex selection
        if sex != None:
            siblings = [x for x in siblings if x.sex == sex]
        if len(siblings) != 0:
            #If there are siblings, rank by age and select their chidlren
            siblings.sort(reverse=True,key=lambda x:x.age)
            for sibling in siblings:
                #Check whether each sibling has children
                children = kinship.get_children(sibling)
                if sex != None:
                    children = [x for x in children if x.sex == sex]
                if children != []:
                    #If the sibling has children, check for the alive children
                    select = [x for x in children if x.lifestatus == alive]
                    select.sort(reverse=True,key=lambda x:x.age)
                    heirs.append(select)
                else:
                    pass # Otherwise, no children
            # Every sibling has been checked
    return heirs    


def find_heirs_brothers_sons_oldest_to_youngest(person):
    """Return the sons of a Person's brothers, ranked by age.
    
    The ranking is both by brothers age and then by their children's age.
    
    .. deprecated::
        `find_heirs_brothers_sons_oldest_to_youngest` derives from the original
        simulation, but `find_heirs_siblings_children_oldest_to_youngest` is 
        the preferred. This function will eventually be replaced with a mapping
        to that function.
        

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
    siblings = kinship.get_siblings(person)
    if siblings != []:
        #If there are siblings, select the brothers
        select_brothers = [x for x in siblings if x.sex == male]
        if len(select_brothers) != 0:
            #If there are brothers, rank by age and select their chidlren
            select_brothers.sort(reverse=True,key=lambda x:x.age)
            for brother in select_brothers:
                #Check whether each brother for sons
                children = kinship.get_children(brother)
                if children != []:
                    #If the brother has children, check for the alive male children
                    select = [x for x in children if x.sex == male and x.lifestatus == alive]
                    select.sort(reverse=True,key=lambda x:x.age)
                    heirs.append(select)
                else:
                    pass # Otherwise, no children
            # Every brother has been checked
    return heirs

def find_heirs_multiple_constructor(*args):
    """Generate a new find_heirs function out of multiple find_heirs functions.
    
    Given a variable length list of find_heirs functions, a new find_heirs
    function is constructed by running each function sequentially and then 
    returning the combined output of them in the order provided.    

    Parameters
    ----------
    *args : callable
        All find_heirs or equivalent functions, to be combined.

    Returns
    -------
    callable
        returns a new function that takes person as an argument; this is the 
        input to the actual InheritanceRuleComplex or equivalent class.
    """
    #Check that all args are in fact callable
    for f in args:
        if callable(f) == False:
            raise TypeError(str(f) + ' is not callable')
    def find_heirs_multiple(person):
        """Find_heirs combining multiple basic find_heirs functions.
        
        A custom function generated by `find_heirs_multiple_constructor` which 
        will now work as a `find_heirs` function.

        Parameters
        ----------
        person : Person
            The person whose heirs are to be found.

        Returns
        -------
        list of Person or list of list of Person
            The heirs of a person
        """
        if isinstance(person,main.Person) == False:
            raise TypeError('person not Person')
        output = []
        for f in args:
            #For each function, get heirs
            heirs = f(person)
            if heirs == None or heirs == []:
                pass
            elif isinstance(heirs,main.Person):
                #Person, so add double brackets and then add
                output += [[heirs]]
            elif all([x == [] for x in heirs]):
                pass
            elif type(heirs) == list and isinstance(heirs[0],main.Person):
                #list of Persons, add brackets then 
                output += [heirs]
            elif type(heirs) == list and type(heirs[0]) == list and any([isinstance(y,main.Person) for x in heirs for y in x]):
                #list of lists of person, just add
                output += heirs
            else:
                raise ValueError('heirs returned not valid')
        return output
    return find_heirs_multiple

#Limitation of heirs
def limit_heirs_none(heirs):
    """Impose no limits on heirs.
    
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
    """Limit heirs to only have one house.
    
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
        if any([isinstance(y,main.Person) for x in heirs for y in x]) == False:
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

def limit_heirs_by_age(heirs,age_of_majority):
    """Limit heirs to those at or above an age of majority.
    
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
        if any([isinstance(y,main.Person) for x in heirs for y in x]) == False:
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

def limit_heirs_multiple_constructor(*args):
    """Create a new limit_heirs function that iterates over other limit_heirs functions.

    Parameters
    ----------
    *args : callables
        Other limit_heirs functions to be iterated over in succession

    Returns
    -------
    callable
        Returns a new limit_heirs funcitons

    """
    for f in args:
        if callable(f) == False:
            raise TypeError(str(f) + ' is not callable')
    def limit_heirs_multiple(heirs):
        """Limit heirs based on a sequence of other functions.
        
        A custom `limit_heirs` function that combines others and iterates
        over them.

        Parameters
        ----------
        heirs : list of Person or list of list of Person
            heirs, the return argument of find_heirs type functions

        Returns
        -------
        list of Person or list of list of Person
            The remaining heirs of a person
        """
        if isinstance(person,main.Person) == False:
            raise TypeError('person not Person')
        for f in args:
            #For each function, get the new remainingheirs
            heirs = f(heirs)
            if heirs == [] or all([x == [] for x in heirs]):
                return []              
        return heirs
    return limit_heirs_multiple

#Distribution of property and moving families/households
def distribute_property_to_first_heir_and_move_household(person,heirs):
    """Give property to a single heir then move the heir's household into the new house.
    
    The old heir doesn't have to give up their old house, they just can't live there anymore.
    If they are inheriting multiple houses, they move to the last one
    
    Parameters
    ----------
    person : Person
        The Person who has died and whose property needs to be moved
    heirs : list of Person, list of lists of Person, or Person
        The Person(s) who will inherit and will become the owner of the property.
        
    Returns
    -------
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
    for h in person.has_community.has_world.houses:
        if person in h.get_owners():
            h.change_owner(person, heir)
            #old_house = heir.has_house
            behavior.mobility.move_household_to_new_house(heir,h)
            transfer_happened = True
    return transfer_happened

#What happens if inheritance fails?
def failed_inheritance_no_owner(person):
    """IF no one inherits, then the property defaults to no owner.
    
    Parameters
    ----------
    person : Person
        The person whose property must be changed to none
    
    Returns
    -------
    bool
        Successful?
    """
    if isinstance(person,main.Person) == False:
        raise TypeError('person not a Person')
    transfer_happened = False
    for h in person.has_community.has_world.houses:
        if person in h.get_owners():
            h.remove_share(person)
            transfer_happened = True
    return transfer_happened