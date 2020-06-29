"""A demographic agent-based model of individuals and households

This module implements an object-oriented, agent-based model of how individuals
live and die with empirical life tables and birth rates. It was originally
designed for historical and archaeological modelling, but can be used in a
variety of contexts. Demographic data are based on Bagnall and Frier for
Roman Egypt, and as a result this asusmes a Coale and Demeny style life
table for empirical demography (fertility schedules, marriage eligibility,
and death rates.)

The container for a given simulation is the World, which needs to be set up to contain at least
one Community. The World also provides some pass-through access to the People contained in all
Communities, as well as all Diaries (which record the events of individual lives) via a library.
The World is where each year progresses for all people, resulting in deaths, marriages, moves, 
and births throughout all Communities.

Each Community is started with a given number of Persons and Houses, as well as core 
characteristics for the people (i.e. what their behaviors should be.) Communities are currently
homogeneous to start with, but can become heterogeneous in behavior by migration (mobility) 
between different villages. The planned founders module will enable more heterogeneous starting 
configurations. 

Persons are individual agents with an assigned sex who age and have the option to undergo major 
life events once each year, and in the process develop kinship networks (as well as growing up
within them). Schedules like mortality and fertility schedules are stored in AgeTables.
Persons can be related via birth or marriage as well as through residency in Houses,
and these different types of relationships are explored through the kinship and residency 
modules. Houses are environmental and can only be affected by Persons. Persons (and eventually
Houses) have their histories recorded in Diaries (defined in narrative).
"""

from households import np, rd, scipy, nx, plt, kinship, residency, behavior, narrative
from households.narrative import Diary
from households.identity import *
"""Import the dependency packages defined in households.__init__.py

"""

print('Importing main.py')


class World(object):
    """The world of the simulation.
    
    This contains Community objects and runs the clock.
    
    Attributes
    ----------
    communities : list of Community
        All communities in the simulation.
    library: dict of Diary
        The Diary objects for Persons and Houses in the simulation
    year : int
        The current year. Incremented at the end of each simulation run.
    people : list of Persons
        All living Persons currently in the simulation
    deadpeople : list of Persons
        All dead Persons in the simulation.
    houses : list of House
        All Houses in all communities in the simulation.
    """
    
    def __init__(self):
        self.communities = []
        self.library = {'Person' : [], 'House' : []} #stores the narrative.Diary objects
        self.year = 0
    
    @property
    def people(self):
        """List of people of all constitutent communities."""
        output = []
        if self.communities != []:
            for c in self.communities:
                output.extend(c.people)
        return output
    
    @property            
    def deadpeople(self):
        """List of dead people of all constitutent communities."""
        output = []
        if self.communities != []:
            for c in self.communities:
                output.extend(c.thedead)
        return output
    
    @property            
    def houses(self):
        """List of houses of all constitutent communities."""
        output = []
        if self.communities != []:
            for c in self.communities:
                output.extend(c.houses)
        return output
    
    def add_community(self,community):
        """Add a community to this World.

        Parameters
        ----------
        community : Community
            Community to add to World
        """
        if isinstance(community,Community):
            self.communities.append(community)
            #community.has_world = self
        else:
            raise TypeError('community not type Community')
            
    def add_diary(self,diary):
        """Add a diary object to the library.
        
        Parameters
        ----------
        diary : narrative.Diary
            Diary to be added to the library
        """
        self.library[type(diary.associated).__name__].append(diary)
            
    def progress(self):
        """Progress the world 1 time-step (year).
        
        The order of steps in the simulation follows this schedule:
            1) randomize the order of persons,
            2) death (and thereby inheritance),
            3) mobility,
            4) marriage, 
            5) birth, and 
            6) end the year.
        """
        #Step 1: randomize population order and reset statistics
        rolodex = self.people.copy() #create a copy of the list of people
        rd.shuffle(rolodex) #randomize the order
        
        #Step 2: iterate through each person for death, marriage, and birth
        for p in rolodex:
            #Check if anyone dies, which also runs inheritance and removes them
            ## from houses and teh community
            p.die()
        
        rolodex = self.people.copy() #create a copy of the list of people
        rd.shuffle(rolodex) #randomize the order
        #Now run everything else in turn 
        for p in rolodex:
            #Check for household mobility
            p.leave_home() #runs each person's mobility rule
        rd.shuffle(rolodex) #randomize the order
        #Go through the marriage routine for all persons
        for p in rolodex:
            p.marriage()
        rd.shuffle(rolodex) #randomize the order
        # Go through the birth routine for all persons
        for p in rolodex:
            p.birth()
            
        #Recalculate statistics        
        self.year += 1
        for c in self.communities:
            c.update_stats()
            
    

class Community(object):
    """Communities are collections of Persons living in Houses.
    
    Community is the coresidential living group of Persons who reside in Houses. 

    
    Parameters
    ----------
    world : World
        The world in which this community will exist
    name : str
        The name of the community
    pop : int
        The initial population of the simulation.
    area : int
        The number of houses in the community
    startage : int
        The age at which all persons in the simulation start. Corrected for by burn-in.
    mortab : AgeTable
        An AgeTable storing a Coale and Demeny-style mortality schedule for all people. 
    birthtab : AgeTable
        AgeTable storing probability of giving birth once married by sex (0 for men)
    marriagerule : behavior.marriage.MarriageRule
        This defines how spouses are found and where newlyweds move from behavior.marriage
    inheritancerule : behavior.inheritance.InheritanceRule
        This defines the inheritance rule executed when a Person dies from behavior.inheritance.
    mobilityrule : behavior.mobility.MobilityRule
        This defines the circumstances of mobility from households from behavior.mobility, or a custom function
        
        
    Attributes
    ----------
    name : str
        The name of the community
    has_world : World
        The World this Community is a part of.
      
    houses : list of Houses
        The houses of the community.
    people : list of Persons
        The people who currently live in the community.
    thedead : list of Person
        List of all dead persons, still required for genealogy. 
    
    mortab : AgeTable
        An AgeTable storing a mortality schedule for the community.
    birthtab : AgeTable
        An AgeTable storing probability of giving birth once married (0 for men)
        
    population : int
        The current population of the community.
    area : int
        Number of houses in the community.
    housingcapacity : int
        Total housing Capacity
    """
    
    def __init__(self,world,name,pop,area,startage,mortab,birthtab,marriagerule,inheritancerule,mobilityrule, birthrule):

        self.name = name
        self.has_world = world
        self.has_world.add_community(self)
        
        # Create the houses
        self.area = area #The number of houses to create
        self.houses = []
        for i in range(area):
            self.houses.append(House(10,self)) #Create each house with a maximum number of people who can reside there
        self.housingcapacity = sum([i.maxpeople for i in self.houses])    
        
        #Define dynamics of demography
        if isinstance(mortab,AgeTable) == False:
            raise TypeError('mortab not of type AgeTable')
        self.mortab = mortab # the death table for the community
        if isinstance(birthtab,AgeTable) == False:
            raise TypeError('mortab not of type AgeTable')
        self.birthtab = birthtab #the probability of a woman giving birth at a given age if married
        if isinstance(marriagerule,behavior.marriage.MarriageRule) == False:
            raise TypeError('marriagerule not of type behavior.marriage.MarriageRule')
        if isinstance(inheritancerule,behavior.inheritance.InheritanceRule) == False:
            raise TypeError('inheritance was not behavior.inheritance.InheritanceRule')
        if isinstance(mobilityrule,behavior.mobility.MobilityRule) == False:
            raise TypeError('mobilityrule was not behavior.inheritance.MobilityRule')
        if isinstance(birthrule,behavior.conception.BirthRule) == False:
            raise TypeError('birthrule was not behavior.conception.BirthRule')
        
        # Generate the population
        self.population = pop #The number of individuals to start in the community
        # populate the community
        self.people = []
        for i in range(pop):
            self.people.append(Person(rd.choice([male,female]),startage,self,None,marriagerule,inheritancerule, mobilityrule, birthrule)) #Generate a new person with age startage
            #NB: currently a 50-50 sex ratio, should be customisable. Consider for expansion. 
        self.thedead = [] #store the list of dead Persons
        
    def update_stats(self):
        """Update the statistics for the community at the end of each year.
        """
        self.population = len(self.people)
        self.area = len(self.houses)
        self.housingcapacity = sum([i.maxpeople for i in self.houses])
        


class Person(object):
    """A representation of a human with a social structure and kinship.
    
    Create a new Person in the Community.
    
    Parameters
    ----------
    sex : Sex
        The sex of the person assigned at creation.
    age : int
        Age of the individual assigned at creation, then aging regularly.
    has_community : Community
        The Community to which this individual belongs. Required because of founder problems.
    has_house : House
        The house in which this individual resides. 
    marriagerule : behavior.marriage.MarriageRule
        The MarriageRule implemented by this agent.
    inheritancerule : behavior.inheritance.InheritanceRule
        The InheritanceRule implemented by this agent each year.
    mobilityrule : behavior.mobility.MobilityRule
        The MobilityRule implemented by this agent each year.    
    
    Attributes
    ----------
    name : str
        The name of this individual. Used for narrative.
    sex : identity.Sex
        The sex of the person assigned at creation.
    age : int
        Age of the individual assigned at creation, then aging regularly.
    has_community : Community
        The Community to which this individual belongs.
    has_house : House
        The house in which this individual resides.
    lifestatus : identity.LifeStatus
        Records whether the Person is dead or alive.
    marriagestatus : identity.MarriageStatus
        The marriage status of the individual.
    has_parents : list of Person
        The parents of this individual
    has_spouse : {None, Person}
        The spouse of this individual.
    has_children : list of Person
        The children of this individual
    birthyear : int
        The year this individual was born.   
    marriagerule : behavior.marriage.MarriageRule
        The MarriageRule implemented by this agent.
    inheritancerule : behavior.inheritance.InheritanceRule
        The InheritanceRule implemented by this agent each year.
    mobilityrule : behavior.mobility.MobilityRule
        The MobilityRule implemented by this agent each year.  
    diary : narrative.Diary
        The diary of this individual that records life events.
    """
    
    #Note: remarriage needs to be added as an option
    def __init__(self, sex, age, has_community, has_house, marriagerule, inheritancerule, mobilityrule, birthrule):
        self.sex = sex
        if sex == male:
            self.name = rd.choice(narrative.male_names)
        else:
            self.name = rd.choice(narrative.female_names)
        self.age = age
        self.has_community = has_community #link to the community
        self.has_house = has_house #link to their house
        self.marriagerule = marriagerule
        self.inheritancerule = inheritancerule
        self.mobilityrule = mobilityrule
        self.birthrule = birthrule
        
        self.lifestatus = alive
        self.marriagestatus = ineligible #Variable to store marriage status
        self.has_spouse = None #The individual to whom this individual is married
        self.has_parents = []
        self.has_children = []
        
        self.birthyear = self.has_community.has_world.year - age
        self.diary = Diary(self)
        self.has_community.has_world.add_diary(self.diary)
        self.diary.add_event(narrative.BornEvent)

        
    def die(self):
        """Check whether this Person dies or ages 1 year.
        
        Checks the community mortality table for this individual. If the individual
        lives, they age one year. Otherwise, they die, inheritance takes place, and
        the Person is removed from the house.
        """
        #figure out if this person dies
        r = self.has_community.mortab.get_rate(self.sex,self.age)
        if r <= rd.random(): #stay alive
            self.age += 1
        else: #if this person died this year, toggle them to be removed from the community
            self.__dies__()
    
    def __dies__(self):
        """Actually does the work of dying."""
        self.lifestatus = dead
        self.diary.add_event(narrative.DeathEvent)
        if self.marriagestatus == married:
            self.has_spouse.marriagestatus = widowed
        self.inheritancerule(self)
        if self.has_house is not None:
            self.has_house.remove_person(self)
        self.has_community.thedead.append(self.has_community.people.remove(self))

    def marriage(self):
        """Check whether this person gets married this timestep.
        
        This step determines marriage eligibility, as well as finding potential
        candidates for marriage. All of this occurs through the MarriageRule.
        """
        if self.marriagestatus == married: #if married, don't run this script
            pass
        elif self.marriagestatus == unmarried: #if this person is eligible to be married
            #run the marriage rules
            self.marriagerule(self)
            if self.marriagestatus == married: #if successful, record it
                self.diary.add_event(narrative.MarriageEvent,self.has_spouse)
                self.has_spouse.diary.add_event(narrative.MarriageEvent,self)
        elif self.marriagestatus == ineligible: #if none (== too young for marriage), check eligibility
            e = self.marriagerule.eligibility_agetable.get_rate(self.sex,self.age)
            if rd.random() < e: #If eligibility possible, change staus
                self.marriagestatus = unmarried
        elif self.marriagestatus == widowed:
            r = self.marriagerule.remarriage_agetable.get_rate(self.sex,self.age)
            if rd.random() < r:
                self.marriagestatus = unmarried
        else:
            raise ValueError('marriagestatus not of identity.MarriageStatus')
    
    def birth(self):
        """Determine whether this person gives birth.
        
        This relies on the fertility schedule in self.has_community.birthtab to decide
        whether a married woman gives birth this year. If so, this method creates that 
        child in the same house.        
        """
        self.birthrule(self)
                
    def __gives_birth__(self, sex, father):
        """Actually create a new person. Returns the child"""
        child = Person(sex,0,self.has_community,self.has_house,self.marriagerule,self.inheritancerule, self.mobilityrule, self.birthrule) #currently maternal transmission of inheritance rules
        if father != None:
            child.has_parents = [self,father]
            father.has_children.append(child)
        else:
            child.has_parents = [self]
        self.has_children.append(child)
        self.has_community.people.append(child) #add to the community
        self.has_house.add_person(child)
        self.diary.add_event(narrative.BirthEvent,child)
        return child
    
    def leave_home(self):
        """Determine whether this person leaves home through household mobility/fission/migration.
        
        This runs the MobilityRule the person currently has.

        """
        result = self.mobilityrule(self)
        return result

    
                

class House(object):
    """Creates a house in which Persons reside.
    
    The House is an environmental object that doesn't move but can be modified
    by Persons.
    
    Parameters
    ----------
    maxpeople : int
        Maximum number of residents before the house is considered crowded.
    has_community : Community
        The Community in which this house was built


    Attributes
    ----------
    maxpeople : int
        Maximum number of residents before the house is crowded. Currently no 
        repercussion for a crowded house.
    rooms : int
        Number of rooms in the house. An alternative way of thinking about space.
    has_community : Community
        The Community in which this house was built.
    people : list of Person
        List of the people who reside in the house.
    owner : Person
        The person who owns this house. Assumes single or primary ownership.
    address : str
        The name of the house, to make individuality clearer in narrative.
    """
    
    #EVENTUALLY, houses may be expanded, change through time, have value,
    ## require maintenance, etc. 
    def __init__(self,maxpeople,has_community):
        self.maxpeople = maxpeople
        self.rooms = 1
        self.has_community = has_community
        self.people = []
        self.owner = None #pointer to the person who owns the house
        self.address = str(rd.randrange(1,101,2)) + ' ' + rd.choice(narrative.address_names) 
        self.diary = Diary(self)
        self.has_community.has_world.add_diary(self.diary)
    
    def add_person(self,tobeadded):
        """Add a person to the house.
        
        Parameters
        ----------
        tobeadded : Person
            The person to be added to the residents of the house.
        """
        self.people.append(tobeadded)
        tobeadded.diary.add_event(narrative.EnterhouseEvent)
        tobeadded.has_house = self
    
    def remove_person(self,toberemoved):
        """Remove a person from the house.
        
        Parameters
        ----------
        toberemoved : Person
            The person to be removed from the residents of the house
        """
        self.people.remove(toberemoved)
        toberemoved.diary.add_event(narrative.LeaveHouseEvent)
        toberemoved.has_house = None
        

class AgeTable(object):
    """Store age-specific annual rates of death, marriage, birth, etc.
    
    AgeTables create a schedule of age- and sex- dependent annual rates of 
    different phenomena, literally anything from marriage eligibility to death.
    
    Parameters
    ----------
    ages : list
        A list of ages to define the relevant intervals over which rates change.
        Each interval includes the lower bounds, such that each is defined by
        ages[i] <= x < ages[i+1].
    sex1, sex2 : Sex
        The variables defining which rates correspond to which sex.
    rates1, rates2 : list
        Annual chance of occurence for each interval. n.b. that len(rates) - len(ages) - 1  
    """
    
    def __init__(self,ages,sex1,rates1,sex2,rates2):
        self._ages = ages
        self._sex1 = sex1
        self._rates1 = rates1
        self._sex2 = sex2
        self._rates2 = rates2  
        
    def get_rate(self,sex,age):
        """Return the annual rate for a given sex and age.

        Parameters
        ----------
        sex : Sex
            The sex in the table to be consulted.
        age : int
            The age of the individual. Must be within defined range of table.
 
        Returns
        -------
        float
            The rate for that age and sex.
            
        """
        i = [i for i in range(len(self._ages)-1) if age>=self._ages[i] and 
        age<self._ages[i+1]][0]
        if sex == self._sex1:
            return self._rates1[i]
        else:
            return self._rates2[i]
        
    def NullAgeTable():
        """Define a null AgeTable.
        """
        return AgeTable([0,1000],male,[0],female,[0])

##Example code
if __name__ == '__main__':
    pass

