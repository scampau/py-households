
"""A demographic agent-based model of individuals and households

This module implements an object-oriented, agent-based model of how individuals
live and die with empirical life tables and birth rates. It was originally
designed for historical and archaeological modelling, but can be used in a
variety of contexts. Demographic data are based on Bagnall and Frier.





"""

from households import np, rd, scipy, nx, plt, kinship, residency, behavior, narrative
from households.narrative import Diary
from households.identity import *
"""Import the dependency packages defined in households.__init__.py

"""

print('Importing main.py')


class World(object):
    """The world of the simulation.
    
    This contains Community objects and will run the clock. Currently
    unimplmented.
    """
    
    def __init__(self):
        self.communities = []
    
    @property
    def people(self):
        output = []
        if self.communities != []:
            for c in self.communities:
                output.extend(c.people)
        return output
                
    def deadpeople(self):
        pass #to be implemented
    
    def add_community(self,community):
        """Add a community to this World.

        Parameters
        ----------
        community : Community
            Community to add to World
        """
        if isinstance(community,Community):
            self.communities.append(community)
        else:
            raise TypeError('community not type Community')
            
    def progress(self):
        """Progress the simulation one year.

        Returns
        -------
        None.

        """
    

class Community(object):
    """Communities are collections of people and houses following a schedule.
    
    community is both the storage for people living in houses and the container
    for the simulation that runs the schedule of the year.
    
    Note: this doc-string is out of date and needs to be updated.
    
    Parameters
    ----------
    name : str
        The name of the community
    pop : int
        The initial population of the simulation
    area : int
        The number of houses in the community
    startage : int
        The age at which all persons in the simulation start. Corrected for by burn-in.
    mortab : AgeTable
        An AgeTable storing a Coale and Demeny-style mortality schedule
    marrtab : AgeTable
        AgeTable storing marriage eligiblity probability by age and sex
    birthtab : AgeTable
        AgeTable storing probability of giving birth once married by sex (0 for men)
    marriagerule : callable
        This defines the location newlyweds move to from behavior.marriage, or a custom function.
    inheritance : behavior.inheritance.InheritanceRule
        This defines the inheritance rule  from behavior.inheritance, or a custom function.
    mobilityrule : callable
        This defines the circumstances of houshold fissioning from behavior.mobility, or a custom function
        
        
    Attributes
    ---------
    name : str
        The name of the community
    year : int
        The year of the simulation of this community.
    area : int
        Number of houses in the community.
    population : int
        The current population of the community.
    housingcapacity : int
        The total housing capacity of the community in terms of people.
    births : int
        Total births this year.
    marriages : int
        Total marriages this year.
    deaths : int
        Total deaths this year.
    occupied : int
        Number of occupied houses.        
        
    houses : list of House objects
        The houses of the community.
    people : list of Person objects
        The people who currently live in the community.
    
    mortab : AgeTable
        An AgeTable storing a mortality schedule for the community.
    marrtab : AgeTable
        An AgeTable storing marriage eligiblity probability by age and sex
    birthtab : AgeTable
        An AgeTable storing probability of giving birth once married by sex (0 for men)
    marriagerule : marriage.MarriageRule
        This defines the location newlyweds move to from behavior.marriage, or a custom function.
    mobilityrule : callable
        This defines the circumstances of houshold fissioning from behavior.mobility, or a custom function
        
    thedead : list
        List of all dead persons, still required for genealogy.
    deathlist : list of int
        History of deaths per year.
    birthlist : list of int
        History of births per year.
    marriedlist : list of int
        History of number of marriages per year.
    poplist : list of int
        History of population by year.
    arealist : list of int
        History of number of houses per year.
    occupiedlist : list of int
        History of number of occupied houses per year.        
    """
    
    #global male, female
    def __init__(self,name,pop,area,startage,mortab,birthtab,marriagerule,inheritancerule,mobilityrule):
        
        self.year = 0
        self.name = name
        
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

        
        # Generate the population
        self.population = pop #The number of individuals to start in the community
        # populate the community
        self.people = []
        for i in range(pop):
            self.people.append(Person(rd.choice([male,female]),startage,self,None,marriagerule,inheritancerule,mobilityrule)) #Generate a new person with age startage
            #NB: currently a 50-50 sex ratio, should be customisable. Consider for expansion. 

        #Define statistics to keep track of each step
        self.deaths = 0
        self.births = 0
        self.occupied = 0 # Occupied houses
        self.marriages = 0
        self.moves = 0 #events that track mobility
                
        #Define history of the statistics
        self.thedead = [] #store the list of dead persons
        self.deathlist = [self.deaths]
        self.birthlist = [self.births]
        self.poplist = [self.population]
        self.arealist = [self.area]
        self.occupiedlist = [self.occupied]
        self.marriedlist = [self.marriages]
        
    def progress(self):
        """Progress the community 1 time-step (year).
        
        The order of steps in the simulation follows this schedule:
            1) randomize the order of persons,
            2) death (and thereby inheritance),
            3) mobility,
            4) marriage, 
            5) birth, and 
            6) recalculate all statistics and end the year.
        """
        
        #Step 1: randomize population order and reset statistics
        rd.shuffle(self.people)
        self.deaths = 0
        self.births = 0
        self.moves = 0
        
        #Step 2: iterate through each person for death, marriage, and birth
        for x in self.people:
            x.die()
            
        #Remove the dead from the community
        remove = [i for i in range(len(self.people)) if self.people[i].lifestatus == dead]
        remove.reverse()
        for i in remove:
            self.thedead.append(self.people.pop(i))
            #This simultaneously adds a person to thedead and removes them from people
            self.deaths += 1
            
        #Check for household mobility
        for p in self.people:
            r = p.leave_home() #runs each person's fission rule
            self.moves += int(r)
        
        #Go through the marriage routine for all persons
        for p in self.people:
            p.marriage()
            
        # Go through the birth routine for all persons
        for p in self.people:
            p.birth()
            
        #Recalculate statistics
        self.population = len(self.people)
        self.births = len([1 for x in self.people if x.age == 0])
        self.occupied = len([x for x in self.houses if x.people != []])
        self.deathlist.append(self.deaths)
        self.birthlist.append(self.births)
        self.poplist.append(self.population)
        self.arealist.append(self.area)
        self.occupiedlist.append(self.occupied)
        self.marriages = len([x for x in [p for p in self.people if p.marriagestatus == married] if x.has_spouse.lifestatus == alive])
        self.marriedlist.append(self.marriages)
        
        self.year += 1
    
    #Deprecated function, will be removed
    # def get_eligible(self,person):
    #     """Returns list of all eligible marriage partners of the opposite sex.
        
    #     Searches through all 
        
    #     Parameters
    #     ----------
        
    #     """
        
    #     candidates = []
    #     relations = kinship.get_siblings(person) 
    #     #Note at present that this only accounts for direct incest; a flexible
    #     ## incest rule would be a useful expansion here. 
    #     if relations == None: relations = []
    #     for x in self.people:
    #         if x.sex != person.sex:
    #             #If unmarried and not a sibling
    #             if x.marriagestatus == unmarried and (x in relations) == False:
    #                 candidates.append(x)
    #     return candidates                    


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
        The Community to which this individual belongs.
    has_house : House
        The house in which this individual resides.
    
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
    """
    
    #Note: remarriage needs to be added as an option
    def __init__(self,sex,age,has_community,has_house,marriagerule,inheritancerule, mobilityrule):
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
        
        self.lifestatus = alive
        self.marriagestatus = ineligible #Variable to store marriage status
        self.has_spouse = None #The individual to whom this individual is married
        self.has_parents = []
        self.has_children = []
        
        self.birthyear = self.has_community.year
        
        # Options for married include None (too young for marriage), False 
        ## (old enough but not eligible yet), or True (yes or widowed)
        
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
            self.lifestatus = dead
            if self.marriagestatus == married:
                self.has_spouse.marriagestatus = widowed
            self.inheritancerule(self)
            if self.has_house is not None:
                self.has_house.remove_person(self)

    def marriage(self):
        """Check whether this person gets married this timestep.
        
        This step determines marriage eligibility, as well as finding potential
        candidates for marriage. At present the algorithm guarantees marriage
        if there are any eligible candidates of the opposite sex. 
        """
        
        if self.marriagestatus == married: #if married, don't run this script
            pass
        elif self.marriagestatus == unmarried: #if this person is eligible to be married
            #run the marriage rules
            self.marriagerule(self)
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
        
        if self.sex == female and [self.has_spouse.lifestatus if self.marriagestatus == married else dead][0] == alive: #If married, husband is alive, and self is a woman
            b = self.has_community.birthtab.get_rate(self.sex,self.age)
            if rd.random() < b: # if giving birth
                # Create a new child with age 0
                child = Person(rd.choice([male,female]),0,self.has_community,self.has_house,self.marriagerule,self.inheritancerule, self.mobilityrule) #currently maternal transmission of inheritance rules
                child.has_parents = [self,self.has_spouse]
                self.has_children.append(child)
                self.has_spouse.has_children.append(child)
                self.has_community.people.append(child) #add to the community
                self.has_house.add_person(child)
    
    def leave_home(self):
        """Determine whether this person leaves home through household mobility/fission/migration.

        """
        result = self.mobilityrule(self)
        return result
    
                

class House(object):
    """Creates a house in which persons reside.
    
    Parameters
    ----------
    maxpeople : int
        Maximum number of residents before the house is crowded. Currently no 
        repercussion for a crowded house.
    has_community : Community
        The Community in which this house was built


    Attributes
    ----------
    maxpeople : int
        Maximum number of residents before the house is crowded. Currently no 
        repercussion for a crowded house.
    rooms : int
        Number of rooms in the house. An alternative way of thinking about space.
        Currently no repercussions.
    has_community : Community
        The Community in which this house was built
    people : list of Person
        List of the people who reside in the house.
    owner : Person
        The person who owns this house. Assumes single or primary ownership.
    address : str
        The name of the house, to make individuality clearer
    """
    
    #Houses belong to the community, have an owner, contain people
    #EVENTUALLY, houses may be expanded, change through time, etc. 
    def __init__(self,maxpeople,has_community):
        self.maxpeople = maxpeople
        self.rooms = 1
        self.has_community = has_community
        self.people = []
        self.owner = None #pointer to the person who owns the house
        self.address = str(rd.randrange(1,101,2)) + ' ' + rd.choice(narrative.address_names) 
        
    
    def add_person(self,tobeadded):
        """Add a person to the house.
        
        Parameters
        ---------
        tobeadded : Person
            The person to be added to the residents of the house.
        """
        self.people.append(tobeadded)
        tobeadded.has_house = self
    
    def remove_person(self,toberemoved):
        """Remove a person from the house.
        
        Parameters
        ---------
        toberemoved : Person
            The person to be removed from the residents of the house
        """
        self.people.remove(toberemoved)
        toberemoved.has_house = None
        

class AgeTable(object):
    """AgeTables store age-specific annual rates of death, marriage, birth, etc.
    
    AgeTables create a schedule of age- and sex- dependent annual rates of 
    different phenomena, literally anything from marriage eligibility to death.
    
    Parameters
    ----------
    ages : list
        A list of ages including the lower bounds, such that ages[0] <= x < ages[1] is the comparison.
    sex1, sex2 : Sex
        The variables defining which rates correspond to which sex.
    rates1, rates2 : list
        Annual chance of occurence for each interval. n.b. that len(rates) - len(ages) - 1
    
    Attributes
    ----------
    
    
    """
    #global male, female

    def __init__(self,ages,sex1,rates1,sex2,rates2):
        self._ages = ages
        self._sex1 = sex1
        self._rates1 = rates1
        self._sex2 = sex2
        self._rates2 = rates2  
        
    def get_rate(self,sex,age):
        """Returns the annual rate for a given sex and age.

        Parameters
        ----------
        sex : Sex
            The sex in the table to be consulted.
        age : int
            The age of the individual. Must be within defined range of table
 
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
        """Defines a null AgeTable.
        """
        return AgeTable([0,1000],male,[0],female,[0])

##Example code
if __name__ == '__main__':
    pass
    # #Life tables are Coale and Demeny: Male, west 4, female west 2, .2% annual increase. See Bagnall and frier
    # maledeath = pd.read_csv('../data/demo/West4Male.csv')
    # ages = list(maledeath.Age1) + [list(maledeath.Age2)[-1]]
    # malerates = list(maledeath[maledeath.columns[2]])
    # femaledeath = pd.read_csv('../data/demo/West2Female.csv')
    # femalerates = list(femaledeath[femaledeath.columns[2]])
    # bagnallfrier = households.AgeTable([0,1] + range(5,105,5), male, malerates, female, femalerates)
    # del maledeath, femaledeath
    
    # examplebirth = AgeTable([0,12,40,50,100],female,[0,.3,.1,0],male,[0,0,0,0,0])
    
    # examplemarriage = AgeTable([0,12,17,100],female,[0,1./7.5,1./7.5],male,[0,0,0.0866]) #These values based on Bagnall and Frier, 113-4 (women) and 116 (men) for Roman egypt
    
    # def inheritance_moderate(person):
    #     """
    #     Upon the death of the patriarch, the house is given to someone in this
    #     order:
            
    #     Male children in order of age
    #     Children of brothers not in line for succession (have to move into household)
        
    #     This stems from the description of the moderate inheritance regime in Asheri
    #     """
    #     #The moderate inheritance regime of Asheri 1963
    #     # Check if patriarch
    #     if person.sex == male and any([h.owner == person for h in person.comm.houses]):
    #         #First priority: male children
    #         inherited = bhv.inheritance.inherit_sons(person,True) #what about grandchildren?
    #         if inherited == False:
    #             #Second priority: adoption of brothers' younger sons
    #             inherited = bhv.inheritance.inherit_brothers_sons(person)
    #             if inherited == False:
    #                 #If there is still no heir, for now the ownership defaults
    #                 bhv.inheritance.inherit(person,None)    
    # def brother_loses_out_15(house):
    #     if house.people != [] and house.owner != None:
    #         bhv.mobility.brother_loses_out(house,15)
                
    # #An example of a single basic run
    # testcase = Community(500,500,12,bagnallfrier,examplemarriage,examplebirth,bhv.locality.patrilocality,inheritance_moderate,brother_loses_out_15)
    # houstory = {}
    # for h in testcase.houses:
    #     houstory[h] = {'classify' : [],'pop' : []}
    # for i in range(200):
    #     testcase.progress()
    #     for h in testcase.houses:
    #         houstory[h]['classify'].append(residency.classify_household(h))
    #         houstory[h]['pop'].append(len(h.people))
    # plt.plot(testcase.poplist)
    
    # #Plot the changing types of houses
    # array = []
    # labels = ['empty','solitary','no-family','nuclear','extended','multiple']
    # which = lambda x: [i for i in range(len(labels)) if labels[i] == x][0]
    # for y in range(testcase.year):
    #     new = [0.]*6
    #     for k in houstory.keys():
    #         w = which(houstory[k]['classify'][y])
    #         new[w]+=1
    #     new = [x*1./sum(new[1:]) for x in new[1:]]       
    #     array.append(new)
    # plt.stackplot(range(testcase.year),np.transpose(array),baseline='zero')
    # plt.axis([0,300,0,1])
    
    # #An example of a repetition script
    # record = []
    # repeat = 50
    # years=200
    # for r in range(repeat):
    #     rd.seed()
    #     testcase = Community(500,500,12,west2male,examplemarriage,examplebirth,bhv.locality.patrilocality,inheritance_moderate,brother_loses_out_15)
    #     houstory = {}
    #     for h in testcase.houses:
    #         houstory[h] = []
    #     for i in range(years):
    #         testcase.progress()
    #         for h in testcase.houses:
    #             houstory[h].append(classify_household(h))
    #     record.append(testcase.poplist)
    
    # for i in record:
    #     plot(i)
    
    # window = 20
    # meancorr = []
    # for y in range(years-window):
    #     count = 0
    #     meancorr.append(0.)
    #     for i in range(repeat):
    #         for j in range(i):
    #             if j != i:
    #                 meancorr[y] += corrcoef([record[i][x] for x in range(y,y+window)],[record[j][x] for x in range(y,y+window)])[0][1]
    #                 count +=1
    #     meancorr[y] = meancorr[y]/count
        
                    
    
    
        
        
        
    #     owner_dead = [h for h in [h for h in testcase.houses if h.owner is not None] if h.owner.lifestatus == dead]
    #     if len(owner_dead) > 0:
    #         print('Something has gone wrong')
    #         break
    # plot_classify(testcase.houses)
    
    # df = pd.DataFrame({'classify' : [classify_household(h) for h in testcase.houses if len(h.people)>0], 'size' : [len(h.people) for h in testcase.houses if len(h.people)>0]})
    # groups = df.groupby('classify')
    # groups.mean()
