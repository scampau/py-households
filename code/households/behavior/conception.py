"""Determine how women in the community give birth.

Birth rates are variable between populations, but so are other fertility and
conception related decisions and impacts such as infanticide, maternal death,
etc.
"""

from households import np, rd, scipy, nx, plt, inspect, kinship, residency, main, behavior
from households.identity import *

class BirthRule(behavior.main.Rule):
    """Each year, check whether this Person gives birth.
    
    Each year, this person needs to consult the relevant fertility schedule
    depending on whether she is married. If she gives birth, the sex of the 
    child depends on the sex ratio, and whether the mother survives birth is 
    determined too.
    
    Parameters
    ----------
    marriedbirth : main.AgeTable
        Fertility rate for a woman in a marriage.
    unmarriedbirth : main.AgeTable
        Fertility rate for a woman not in a marriage.
    femalesexratio : float
        Percentage of the population born women.
    maternaldeath : callable
        Returns whether a woman dies because of childbirth complications.
    infanticide : callable
        Returns whether the child is killed/exposed rather than 
    """
    
    def __init__(self, marriedbirth, unmarriedbirth, femalesexratio, maternaldeath, infanticide):
        