"""Determines schedules of marriage and remarriage as well as locality by newlyweds.

The marriage module encodes several overlapping options for how marriage can function.
This is enacted through the MarriageRule class each Person has, which determines:

    1. when they can transition from `ineligible` to `unmarried` (and are thus
        eligible for marriage),
    2. how they identify eligible partners, 
    3. how they pick a spouse within that pool,
    4. if they marry someone, where they relocate to, and
    5. if they are widowed/are a widower, will they be allowed to remarry.
    
Together, these concepts form a single behavior that can be transmitted and 
learned.
"""

from households import np, rd, scipy, nx, plt,inspect, kinship, residency, main, behavior
from households.identity import *
print('importing marriage')
#import kinship as kn

class MarriageRule(behavior.Rule):
    """Define marriage rules for individuals.
    
    The process of getting married involves:
        1) identifying the pool of who could be married
        2) finding someone within that pool to marry
        3) deciding where to move with them
    
    These three steps can be thought of as eligiblity determination, mate choice, and locality.
    The only universal is that both agents must fit each other's standards.
    This means that Dolores must consider Teddy eligible from her get_eligible
    function, and Teddy must consider Dolores eligible from his get_eligible 
    function.
    
    MarriageRule also defines the eligibility agetable,  which defines when a 
    person becomes eligible for marriage, as well as the remarriage AgeTable.
    
    Functions that can be used for get_eligible, pick_spouse, and locality
    have prefixes as such in this module.
    
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
    eligibility_agetable : main.AgeTable
        The schedule for becoming eligible for marriage.
    remarriage_agetable : main.AgeTable
        Whether a Person is allowed to remarry and at what ages. 
    """
    def __init__(self, eligibility_agetable,get_eligible,pick_spouse,locality,remarriage_agetable):
        for f, a in zip([get_eligible,pick_spouse,locality],[1,1,2]):
            if self.__verify_callable__(f,a) == True:
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
        """Find a person to marry and marry them.

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
        """Marry the two people.

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
        """Return whether persontwo is in personone's definitions of eligibility.
        
        This should be called by persontwo if they wish to marry personone using 
        personone's marriage rule to ensure that they are compatible in their eligiblity.
        
        Parameters
        ----------
        personone, persontwo : main.Person
            The people being compared, namely that persontwo fits personone's ideas of eligibility.

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
    """Get all eligible individuals in the community with an incest prohibition against siblings.
    
    This uses heterosexuality as an assumption to identify eligible individuals.
    
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


#pick spouse functions
def pick_spouse_random(candidates):
    """Choose a spouse at random from the candidates.

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
    
    .. deprecated::
        This function will soon be replaced by a behavior.mobility function.
    
    Parameters
    ----------
    houses : list of House
        The Community.houses list for the community in question, or another 
        subset of houses.
    
    Returns
    -------
    None or House
        Picks an empty house if one exists, otherwise returns None.
    """
    possible_houses = [h for h in houses if len(h.people) == 0 and h.get_owners() == []]
    if len(possible_houses) == 0:
        ## if no houses available
        return None
    else:
        return rd.choice(possible_houses)


def locality_patrilocality(husband,wife):
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
        locality_neolocality(husband,wife,male)
        return False
    elif len(husband.has_house.people)+1 >= husband.has_house.maxpeople:
        #If the house is full, find a new one and move out
        locality_neolocality(husband,wife,male)
        return False
    else:
        #If the house has capacity, the wife moves in with the husband
        behavior.mobility.move_person_to_new_house(wife, husband.has_house)
        return True

def locality_matrilocality(husband,wife):
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
        locality_neolocality(husband,wife,female)
        return False
    elif len(wife.has_house.people)+1 >= wife.has_house.maxpeople:
        #If the house is full, find a new one and move out
        locality_neolocality(husband,wife,female)
        return False
    else:
        #If the house has capacity, the wife moves in with the husband
        behavior.mobility.move_person_to_new_house(husband, wife.has_house)
        return True

def locality_neolocality(husband,wife,primary):
    """Find a new house in the same community as the primary spouse and moves the couple there.
    
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
        new_house.add_share(owner, 1)
        return True
