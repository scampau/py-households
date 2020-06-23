"""Determine how women in the community give birth.

Birth rates are variable between populations, but so are other fertility and
conception related decisions and impacts such as infanticide, maternal death,
etc.
"""

from households import rd, inspect, kinship, residency, main, behavior, identity


class BirthRule(behavior.Rule):
    """Each year, check whether this Person gives birth.
    
    Each year, this person needs to consult the relevant fertility schedule
    depending on whether she is married. If she gives birth, the sex of the 
    child depends on the sex ratio, and whether the mother survives birth is 
    determined too.
    
    Parameters
    ----------
    marriedbirth : main.AgeTable
        Fertility rate for a woman in a marriage. Men is null.
    unmarriedbirth : main.AgeTable
        Fertility rate for a woman not in a marriage. Men is null.
    femalesexratio : float
        Percentage of the population born women.
    maternaldeath : callable
        Returns whether a woman dies because of childbirth complications. Takes
        just her as the argument.
    infanticide : callable
        Returns whether the child is killed/exposed; takes mother and child
        as arguments.
    """
    
    def __init__(self, marriedbirth, unmarriedbirth, femalesexratio, maternaldeath, infanticide):
        
        #Check that callables are properly callable
        for f, a in zip([maternaldeath,infanticide],[1,2]):
            if self.__verify_callable__(f,a) == True:
                pass
            else:
                raise ValueError('wrong number of arguments for '+str(f.__name__))
        self._maternal_death = maternaldeath
        self._infanticide = infanticide
        # Check that agetables are really agetables
        for at in [marriedbirth,unmarriedbirth]:
            if self.__verify_agetable__(at) == True:
                #Check that men is 0
                if at._sex1 == identity.male:
                    if any([x != 0 for x in at._rates1]):
                        raise ValueError("agetable contains non-zero values for male birth rates")
                else:
                    if any([x != 0 for x in at._rates2]):
                        raise ValueError("agetable contains non-zero values for male birth rates")
        self._marriedbirth = marriedbirth
        self._unmarriedbirth = unmarriedbirth
        #Check teh sex ratio
        if type(femalesexratio) == float:
            if 0 <= femalesexratio and femalesexratio <= 1:
                pass
            else:
                raise ValueError("femalesexratio not in [0,1]")
        elif type(femalesexratio) == int and (femalesexratio == 0 | femalesexratio == 1):
            femalesexratio = float(femalesexratio)
        else:
            raise TypeError("femalesexratio not float in range [0,1]")
        self._femalesexratio = femalesexratio
        
    def __call__(self, person):
        """Check whether a person will give birth this year.
        
        Returns whether the person gave birth.
        
        Parameters
        ----------
        person : main.Person
            The person to check and potentially give birth.
        """
        if self.__verify_person__(person) == True:
            pass
        if person.sex != identity.female:
            return False
        #Check if the married or unmarried schedule will be consulted and consult it
        if [person.has_spouse.lifestatus if person.marriagestatus == identity.married else identity.dead][0] == identity.alive:
            r = self._marriedbirth.get_rate(person.sex, person.age)
            father = person.has_spouse
        else:
            r = self._unmarriedbirth.get_rate(person.sex, person.age)
            father = None
        #Check if this person gives birth
        if rd.random() < r:
            #They do. Determine the sex of the child
            if rd.random() < self._femalesexratio:
                sex = identity.female
            else:
                sex = identity.male
            child = person.__gives_birth__(sex, father)
            #Determine whether hte mother dies during childbirth
            if self._maternal_death(person) == True:
                person.__dies__()
            #Determine whether the child is killed by infanticide
            if self._infanticide(person, child) == True:
                child.__dies__()
            return True
        else:
            return False
            
        
def maternal_death_random(mother, rate = .5):
    """Mothers die at a fixed rate during childbirth.
    
    Parameters
    ----------
    mother : main.Person
        The person to check
    rate : float
        The probability a mother dies during childbirth.
        
    Returns
    -------
    bool
        Whether the mother lives or dies
    """
    if rd.random() < rate:
        return True
    else:
        return False

def maternal_death_zero(mother):
    """Mothers never die in childbirth.
    
    Parameters
    ----------
    mother : main.Person
        The mother who won't die
    
    Returns
    -------
    False
    """
    return False

def infanticide_none(mother, child):
    """No infanticide.
    
    Parameters
    ----------
    mother, child : main.Person
        The mother and child to be considered in the infanticide decision
        
    Returns
    -------
    False
        Always false.
    """
    return False

