#############
# Fragmentation

from households import np, rd, sp, nx, plt, kinship, behavior

print('importing fragmentation')

#import kinship as kn
#import inheritance as ih 
#import locality as lc

global male, female
male, female = range(2)

# Each fragmentation function will need to take a household and determine 
## whether anyone in that household needs to leave. If they do, move them.

def no_fragmentation(house):
    """
    No fragmentation rules.
    """
    pass

def brother_loses_out(house,age):
    """
    A (younger) brother who just lost out on the family inheritance leaves the
    house along with his family. Otherwise, people stay put.
    
    house - household to check
    age - age of majority (marriage often) for determining 
    """
    # Check whether any brothers are there
    if house.people != [] and house.owner != None:    
        siblings = kinship.get_siblings(house.owner,house.mycomm.families)
        if siblings != None:
            siblings = [x for x in siblings if x.sex == male and x.age >= age and x.dead == False]
            if len(siblings) > 0:
                for s in siblings:
                    #For each brother who lives in the house
                    if s in house.people:
                        #If there is another brother over the age of majority who is
                        ## not hte ownerwho lives there that person ( and their family)
                        ## moves out
                        # Pick a new house
                        new_house = behavior.locality.get_empty_house(house.mycomm.houses)
                        if new_house != None:
                            # Identify their family and move them
                            behavior.inheritance.move_family(s,new_house)
                        else:
                            # There is no new house, so stay put.
                            pass               
            
    
def house_gets_crowded(house):
    """
    A house that exceeds its capacity gets rid of 1) non-kin of the owner,
    2) more distant kin of the owner.
    """
    pass #To be continued
    
    