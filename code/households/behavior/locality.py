#########################
# Locality functions 

from households import np, rd, scipy, nx, plt, kinship, residency

print('importing locality')
#import kinship as kn

global male, female
male, female = range(2)

def get_empty_house(houses):
    """
    Get a randomly chosen empty house.
    """
    possible_houses = [h for h in houses if len(h.people) == 0 and h.owner == None]
    if len(possible_houses) == 0:
        ## if no houses available
        return None
    else:
        return rd.choice(possible_houses)
    

def patrilocality(husband,wife):
    """
    Changes the house of the couple to that of the husband,
    If none or full, runs neolocality().
    
    husband, wife - the people just married
    
    """
    if husband.myhouse == None:
        #The husband has no house; find a new one
        neolocality(husband,wife)
    elif len(husband.myhouse.people)+1 >= husband.myhouse.maxpeople:
        #If the house is full, find a new one and move out
        neolocality(husband,wife)
    else:
        #If the house has capacity, the wife moves in with the husband
        husband.myhouse.add_person(wife)
        if wife.myhouse is not None: wife.myhouse.remove_person(wife)
        wife.myhouse = husband.myhouse
        

def neolocality(husband,wife,primary=male):
    """
    Finds a new house for a couple. Ownership is given to the primary sex.
    """
    #Select the primary person
    owner = husband if husband.sex == primary else wife
    # Find an empty house
    #rd.shuffle(owner.mycomm.houses) #oh no no no no no no [get out meme]
    new_house = get_empty_house(owner.mycomm.houses)
    if new_house == None:
        # If no house, end
        print('No house found')
        pass #Future extension: if none found, couple may leave community or build
    else:
        # Add husband and wife to house
        new_house.people.extend([husband, wife])
        # Remove from their old houses
        if husband.myhouse is not None:
            husband.myhouse.people.remove(husband)
        if wife.myhouse is not None:
            wife.myhouse.people.remove(wife)
        # make whoever is of the primary sex the owner
        new_house.owner = owner
        # Add a pointed to the house from both individuals
        husband.myhouse = new_house
        wife.myhouse = new_house
