"""Locality decisions for newlyweds.

The locality package encodes options for where a new couple live.
This needs to be renamed marriage or something like it.


"""

from households import np, rd, scipy, nx, plt, kinship, residency
from households.identity import *
print('importing locality')
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
    
    Attributes
    ----------
    
    """
    def __init__(self,get_eligible,pick_spouse,locality):
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
        self.agetable = eligiblity_agetable
        
    def __call__(self,person):
        """

        Parameters
        ----------
        person : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        #get eligible 
        #check that they are all actual matches
        #pick spouse
        #locality
        #bool for whether marriage happened

    def get_reciprocal(self,personone,persontwo):
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

# def get_eligible(self,person):
#         """Returns list of all eligible marriage partners of the opposite sex.
        
#         Searches through all 
        
#         Parameters
#         ----------
        
#         """
        
#         candidates = []
#         relations = kinship.get_siblings(person,self.families) 
#         #Note at present that this only accounts for direct incest; a flexible
#         ## incest rule would be a useful expansion here. 
#         if relations == None: relations = []
#         for x in self.people:
#             if x.sex != person.sex:
#                 #If unmarried and not a sibling
#                 if x.marriagestatus == unmarried and (x in relations) == False:
#                     candidates.append(x)
#         return candidates 

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
    candidates = [p for p in person.has_community.people if p.sex != person.sex and p.marraigestatus == unmarried]
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
        husband.has_house.add_person(wife)
        if wife.has_house is not None: wife.has_house.remove_person(wife)
        wife.has_house = husband.has_house
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
    elif len(husband.has_house.people)+1 >= husband.has_house.maxpeople:
        #If the house is full, find a new one and move out
        neolocality(husband,wife,female)
        return False
    else:
        #If the house has capacity, the wife moves in with the husband
        wife.has_house.add_person(husband)
        if husband.has_house is not None: wife.has_house.remove_person(wife)
        husband.has_house = wife.has_house
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
        new_house.people.extend([husband, wife])
        # Remove from their old houses
        if husband.has_house is not None:
            husband.has_house.people.remove(husband)
        if wife.has_house is not None:
            wife.has_house.people.remove(wife)
        # make whoever is of the primary sex the owner
        new_house.owner = owner
        # Add a pointed to the house from both individuals
        husband.has_house = new_house
        wife.has_house = new_house
        return True
