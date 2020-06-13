"""Marriage decisions for newlyweds.

The marriage package encodes options for where a new couple live.


"""

from households import np, rd, scipy, nx, plt,inspect, kinship, residency, main, behavior
from households.identity import *
print('importing marriage')
#import kinship as kn

#global male, female
#male, female = range(2)

class MarriageRule(object):
    """Defining marriage rules for individuals.
    
    The process of getting married involves:
        1) identifying the pool of who could be married
        2) finding someone within that pool to marry
        3) deciding where to move with them
    
    These three steps can be thought of as eligiblity determination, mate choice, and locality.
    The only universal is that both agents must fit each other's standards.
    
    MarriageRule also defines the eligibility agetable,
    which defines when a person becomes eligible for marriage,
    as well as the remarriage AgeTable.
    
    Parameters
    ----------
    eligibility_agetable : main.AgeTable
        determine whether a person become eligible for marriage    
    get_eligible : callable
        Find all eligible individuals, based only on an input of the person.
    pick_spouse : callable
        Out of those found by get_eligible, if any, pick one
    locality : callable
        One of the locality functions described below (patrilocality, matrilocality,
        neolocality) or equivalent function that determines where people live
    remarriage_agetable : main.AgeTable
        Determines whether individuals can remarry after death. 
    
    Attributes
    ----------
    
    """
    def __init__(self, eligibility_agetable,get_eligible,pick_spouse,locality,remarriage_agetable):
        for f, a in zip([get_eligible,pick_spouse,locality],[[1],[1],[2]]):
            if self.__verify_rule__(f,a) == True:
                pass
            else:
                raise ValueError('wrong number of arguments for '+str(f.__name__))
        self.__get_eligible = get_eligible
        self.__pick_spouse = pick_spouse
        self.__locality = locality
        if isinstance(eligibility_agetable, main.AgeTable) == False:
            raise TypeError('eligibility_agetable not of type main.AgeTable')
        if isinstance(remarriage_agetable, main.AgeTable) == False:
            raise TypeError('remarriage_agetable not of type main.AgeTable')
        self.eligibility_agetable = eligibility_agetable
        self.remarriage_agetable = remarriage_agetable
        
    def __call__(self,person):
        """

        Parameters
        ----------
        person : main.Person
            The person seeking to get married.

        Returns
        -------
        bool
            whether the person got married, and made the changes along the way.

        """
        #get eligible individuals
        candidates = self.__get_eligible(person)
        #check that they are all actual matches who would accept this person back
        ##this could be changed to allow non-reciprocal to take a year and fail
        candidates = [c for c in candidates if c.marriagerule.__get_reciprocal(c,person) == True]
        if len(candidates) == 0:
            #No candidates, so no marriage
            return False     
        #pick spouse and set marriage status
        spouse = self.__pick_spouse(candidates)
        husband, wife = self.__marry(person,spouse)
        #locality
        result = self.__locality(husband,wife)
        #bool for whether marriage happened; result is just whether locality was succesful.
        return True

    def __marry(self,person,spouse):
        """Actually marry the two people

        Parameters
        ----------
        personone, persontwo: main.Person
        
        Returns
        -------
        husband, wife: main.Person
        """
        husband, wife = (person,spouse) if person.sex == male else (spouse,person)
        husband.marriagestatus = married
        husband.has_spouse = wife
        wife.marriagestatus = married
        wife.has_spouse = husband
        return (husband,wife)

    def __get_reciprocal(self,personone,persontwo):
        """Returns whether persontwo is in personone's definitions of eligibility.
        
        This should be called by persontwo if they wish to marry personone using 
        personone's marriage rule to ensure that they are compatible in their eligiblity.
        

        Parameters
        ----------
        person : main.Person
            A person who needs to be 

        Returns
        -------
        bool
            True if compatible, False if not

        """
        for p in [personone,persontwo]:
            if isinstance(p,main.Person) == False:
                raise TypeError('person not Person')
        if (persontwo in personone.marriagerule.__get_eligible(personone)) == True:
            return True
        else:
            return False
            
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
    
        
    
#eligiblity functions
def get_eligible_all_same_community(person):
    """Gets all eligible individuals in the community. No incest prohibition.

    Parameters
    ----------
    person : main.Person
        The person who we are seeking matches for.

    Returns
    -------
    candidates : list of main.Person
        eligible individuals

    """
    if isinstance(person, main.Person) == False:
        raise TypeError('person not Person')
    #get all individuals in the community who are themselves eligible
    candidates = [p for p in person.has_community.people if p.sex != person.sex and p.marriagestatus == unmarried]
    return candidates

def get_eligible_not_sibling_same_community(person):
    """Gets all eligible individuals in the community. Incest prohibition against siblings.

    Parameters
    ----------
    person : main.Person
        The person who we are seeking matches for.

    Returns
    -------
    candidates : list of main.Person
        eligible individuals

    """
    if isinstance(person, main.Person) == False:
        raise TypeError('person not Person')
    #get all individuals in the community who are themselves eligible
    siblings = kinship.get_siblings(person)
    if siblings == []:
        candidates = [p for p in person.has_community.people if p.sex != person.sex and p.marriagestatus == unmarried]
    else:
        candidates = [p for p in person.has_community.people if p.sex != person.sex and p.marriagestatus == unmarried and p not in siblings]
    return candidates


#picking functions
def pick_spouse_random(candidates):
    """

    Parameters
    ----------
    candidates : list of main.Person
        Potential candidates who match

    Returns
    -------
    spouse
        Chosen individual to marry
    """
    spouse = rd.choice(candidates)
    return spouse


#Locality functions
def get_empty_house(houses):
    """Get a randomly chosen empty house to move into.
    
    Parameters
    ---------
    houses : list of House
        The Community.houses list for the community in question, or another 
        subset of houses.
    
    Returns
    -------
    None or House
        Picks an empty house if one exists, otherwise returns None.
    """
    possible_houses = [h for h in houses if len(h.people) == 0 and h.owner == None]
    if len(possible_houses) == 0:
        ## if no houses available
        return None
    else:
        return rd.choice(possible_houses)


def patrilocality(husband,wife):
    """Newlyweds live at the husband's family's house, or if no house find a new one.
    
    Changes the house of the couple to that of the husband,
    If none or full, runs neolocality().
    
    Parameters
    ----------
    husband, wife : Person
        The people just married, identified by sex.
    
    Returns
    -------
    bool
        True if patrilocality achieved, False if neolocality chosen instead.
    
    """
    if husband.has_house == None:
        #The husband has no house; find a new one
        neolocality(husband,wife,male)
        return False
    elif len(husband.has_house.people)+1 >= husband.has_house.maxpeople:
        #If the house is full, find a new one and move out
        neolocality(husband,wife,male)
        return False
    else:
        #If the house has capacity, the wife moves in with the husband
        behavior.mobility.move_person_to_new_house(wife, husband.has_house)
        return True

def matrilocality(husband,wife):
    """Newlyweds live at the wife's family's house, or if no house find a new one.
    
    Changes the house of the couple to that of the wife,
    If none or full, runs neolocality().
    
    Parameters
    ----------
    husband, wife : Person
        The people just married, identified by sex.
    
    Returns
    -------
    bool
        True if matrilocality achieved, False if neolocality chosen instead.
    
    """
    if wife.has_house == None:
        #The husband has no house; find a new one
        neolocality(husband,wife,female)
        return False
    elif len(wife.has_house.people)+1 >= wife.has_house.maxpeople:
        #If the house is full, find a new one and move out
        neolocality(husband,wife,female)
        return False
    else:
        #If the house has capacity, the wife moves in with the husband
        behavior.mobility.move_person_to_new_house(husband, wife.has_house)
        return True

def neolocality(husband,wife,primary):
    """Finds a new house for a couple. 
    
    Ownership is given to the primary sex.
    
    Parameters
    ----------
    husband, wife : Person
        The people just married, identified by sex.
    primary : Sex
        Defines the sex of the partner who formally owns the property.
    
    Returns
    -------
    bool
        If neolocality achieved, True; False otherwise.
    """
    #Select the primary person
    owner = husband if husband.sex == primary else wife
    # Find an empty house
    new_house = get_empty_house(owner.has_community.houses)
    if new_house == None:
        # If no house, end
        return False
        pass #Future extension: if none found, couple may leave community or build
    else:
        # Add husband and wife to house
        behavior.mobility.move_person_to_new_house(husband, new_house)
        behavior.mobility.move_person_to_new_house(wife, new_house)
        # make whoever is of the primary sex the owner
        new_house.owner = owner
        return True
