import numpy as np
import random as rd
import scipy as sp
import networkx as nx
import matplotlib.pyplot as plt
from kinship import *
from communityrules import *

rd.seed() #Reset the seed

#Define some constants
global male, female
male, female = xrange(2) #values for male and female

class community(object):
    """
    Communities store collections of people and houses.
    
    """
    
    global male, female
    def __init__(self,pop,area,mortab,marrtab,birthtab,locality,inheritance):
        """
        Initialize the community with initial people and houses, as well as demographic dynamics
        
        Initializing a community takes the following:
            pop: the initial population (should be at least 2x that desired)
            area: the number of houses (for now an integer)
            mortab: the agetable for mortality by sex
            marrtab: the agetable for marriage eligibility by sex
            birthtab: the agetable for birth probability once married by sex (e.g. 0 for males at all ages)
        """
        
        self.year = 0
        
        # Create the houses
        self.area = area #The number of houses to create
        self.houses = []
        for i in xrange(area):
            self.houses.append(house(10,self)) #Create each house with a maximum number of people who can reside there
        self.housingcapacity = sum([i.maxpeople for i in self.houses])    
        
        # Generate the population
        self.population = pop #The number of individuals to start in the community
        # populate the community
        self.people = []
        for i in xrange(pop):
            self.people.append(person(rd.choice([male,female]),0,self,None)) #Generate a new person with age 0

        #Define dynamics of demography
        self.mortab = mortab # the death table for the community
        self.marrtab = marrtab #the probability of marriage at a given age by sex
        self.birthtab = birthtab #the probability of a woman giving birth at a given age if married
        self.locality = locality
        self.inheritance = inheritance
        
        #Define a network to keep track of relations between agents
        self.families = nx.DiGraph()
        for individual in self.people:
            self.families.add_node(individual) 
        
        #Define statistics to keep track of each step
        self.deaths = 0
        self.births = 0        
        
        #Define history of the statistics
        self.thedead = [] #store the list of dead agents
        self.deathlist = [self.deaths]
        self.birthlist = [self.births]
        self.poplist = [self.population]
        self.arealist = [self.area]
        

    def progress(self):
        """
        Progress the community 1 year. The order of steps is:
            Death
            Marriage
            Birth
        Inheritance takes place at 
        """
        
        #Step 1: randomize population order and reset statistics
        rd.shuffle(self.people)
        self.deaths = 0
        self.births = 0
        
        #Step 2: iterate through each person for death, marriage, and birth
        for x in self.people:
            x.die()
            
        #Remove the dead from the community
        remove = [i for i in xrange(len(self.people)) if self.people[i].dead == True]
        remove.reverse()
        for i in remove:
            self.thedead.append(self.people.pop(i))
            self.deaths += 1
            
        #Check for household fragmentation here
        
        #Go through the marriage routine for all agents
        for x in self.people:
            x.marriage()
            
        # Go through the birth routine for all agents
        for x in self.people:
            x.birth()
            
        #Recalculate statistics
        self.population = len(self.people)
        self.births = len([1 for x in self.people if x.age == 0])
        self.deathlist.append(self.deaths)
        self.birthlist.append(self.births)
        self.poplist.append(self.population)
        self.arealist.append(self.area)
        
        self.year += 1

    def get_eligible(self,agent):
        """
        Get a list of all living people eligible for marriage of a given sex
        """
        
        candidates = []
        relations = get_siblings(agent,self.families)
        if relations == None: relations = []
        for x in self.people:
            if x.sex != agent.sex:
                #If unmarried and not a sibling
                if x.married == False and (x in relations) == False:
                    candidates.append(x)
        return candidates                    


class person(object):
    """
    A person is an agent with a social structure and kinship.
    
    """
    def __init__(self,sex,age,comm,house):
        """
        Create a new person in the community.
        Sex, age - sex and age at creation of the person (e.g. birth)
        mother, father - references to the person object of the mother and father, else None
        comm - reference to the community the person belongs to.
        house - link to their house
        
        Other variables:
        dead - whether the person is dead or alive
        married - marriage status (None - too young to be married; False - unma-
          rried but eligible; True - married or widowed)
        married_to - Link to the person the agent is married to
        """
        self.sex = sex
        self.age = age
        self.comm = comm #link to the community
        self.house = house #link to their house
        
        self.dead = False
        self.married = None #Variable to store marriage status
        self.married_to = None
        
        self.birthyear = comm.year
        # Options for married include None (too young for marriage), False 
        ## (old enough but not eligible yet), or True (yes)
        
    def die(self):
        """
        Check whether this person dies; if not, they age 1 year.
        
        """
        
        #figure out if this person dies
        r = self.comm.mortab.get_rate(self.sex,self.age)
        if r <= rd.random(): #stay alive
            self.age += 1
        else: #if this person died this year, toggle them to be removed from the community
            self.dead = True
            self.comm.inheritance(self)
            if self.house is not None:
                self.house.remove_person(self)
            
        # Some inheritance rules need to happen here!
        #Note that at present this means that there is no update in the marriage
        ## state of the other person; this means people can only be married 
        ## once.
        
    def marriage(self):
        """
        Check whether this agent gets married this timestep.
        
        """
        
        if self.married == True: #if married, don't run this script
            pass 
        elif self.married == False: #if this agent is eligible to be married
            #get the list of eligible candidates for marriage
            candidates = self.comm.get_eligible(self)
            ##NOTE: evntually this must be adapted to get those not related to a given person by a certain distance
            if len(candidates) != 0: #if there are any eligible people
                choice = rd.choice(candidates) #Pick one
                # Set self as married
                self.married = True
                self.married_to = choice
                #Set the other person as married
                choice.married = True
                choice.married_to = self
                ## Add links to the network of families
                self.comm.families.add_edges_from( [(self,choice,{'type' : 'marriage'}),
                (choice,self,{'type' : 'marriage'})])
                ## Run the locality rules for this community
                husband, wife = (self,choice) if self.sex == male else (choice,self)
                self.comm.locality(husband,wife)
        else: #if none (== too young for marriage), check eligibility
            e = self.comm.marrtab.get_rate(self.sex,self.age)
            if rd.random() < e: #If eligibility possible, change staus
                self.married = False

        
    def birth(self):
        """
        Check whether this agent gives birth to a new child. If so, create that child.
        
        """
        if self.sex == female and [self.married_to.dead if self.married == True else True][0] == False: #If married, husband is alive, and self is a woman
            b = self.comm.birthtab.get_rate(self.sex,self.age)
            if rd.random() < b: # if giving birth
                # Create a new child with age 0
                child = person(rd.choice([male,female]),0,self.comm,self.house)
                self.comm.people.append(child) #add to the community
                self.house.add_person(child)
                # Add the child to the family network
                self.comm.families.add_edge(self,child,{'type' : 'birth'})
                self.comm.families.add_edge(self.married_to,child,{'type' : 'birth'})


    
class house(object):
    """
    Houses are the units in which people reside.
    
    """
    #Houses belong to the community, have an owner, contain people
    #EVENTUALLY, houses may be expanded, change through time, etc. 
    def __init__(self,maxpeople,comm):
        """
        A house can support up to maxpeople individuals before requiring 
        expansion or a family to relocate.
        
        maxpeople - capacity of the house
        comm - pointer to the community
        """  
        self.maxpeople = maxpeople
        self.comm = comm
        self.people = []
        self.owner = None #pointer to the agent who owns the house
    def add_person(self,tobeadded):
        """
        Add a person to the house.
        """
        self.people.append(tobeadded)
    def remove_person(self,toberemoved):
        """
        Remove a person from the house.
        """
        self.people.remove(toberemoved)
        

class agetable(object):
    """
    Agetables are a way of storing age-specific annual rates of phenomena
    such as mortality, pregnacny, marriage, etc.
    
    ages - a list of ages that define intervals
    sex1, sex2 - the represnetations for each sex
    rates1,rates2 - annual rates of occurence for each interval; n.b. len(rates1) = len(ages) - 1 !
    """
    global male, female

    def __init__(self,ages,sex1,rates1,sex2,rates2):
        self.ages = ages
        self.sex1 = sex1
        self.rates1 = rates1
        self.sex2 = sex2
        self.rates2 = rates2  
    def get_rate(self,sex,age):
        """
        Get the annualized rate for a given sex and age from this agetable.
        
        sex - the stardardized male-female representation of each sex
        age - integer number within the valid interval defined for this table
        """
        i = [i for i in xrange(len(self.ages)-1) if age>=self.ages[i] and 
        age<self.ages[i+1]][0]
        if sex == self.sex1:
            return self.rates1[i]
        else:
            return self.rates2[i]





    
    

##Example code
if __name__ == '__main__':
    west2male = agetable([0,1] + range(5,105,5), male, 
    [.38386, .065137, .012644, .009011, .012223, .017511, .019716, .22914, .026903, .03474, .037308, .046951, .056462, .76796, .101664, .139988, .202545, .262221, .361406, .483888, 1],
    female, 
    [.38386, .065137, .012644, .009011, .012223, .017511, .019716, .22914, .026903, .03474, .037308, .046951, .056462, .76796, .101664, .139988, .202545, .262221, .361406, .483888, 1])
    examplebirth = agetable([0,15,50,100],female,[0,.55,0],male,[0,0,0])
    examplemarriage = agetable([0,15,20,100],female,[0,.5,.5],male,[0,0,.5])
    
    record = []
    repeat = 50
    years=300
    for r in xrange(repeat):
        rd.seed()
        testcase = community(1000,500,west2male,examplemarriage,examplebirth,patrilocality,inheritance_moderate)
        for i in xrange(years):
            testcase.progress()
        record.append(testcase.poplist)
    
    for i in record:
        plot(i)
    
    window = 20
    meancorr = []
    for y in xrange(years-window):
        count = 0
        meancorr.append(0.)
        for i in xrange(repeat):
            for j in xrange(i):
                if j != i:
                    meancorr[y] += corrcoef([record[i][x] for x in range(y,y+window)],[record[j][x] for x in range(y,y+window)])[0][1]
                    count +=1
        meancorr[y] = meancorr[y]/count
        
                    
    
    
        
        
        
        owner_dead = [h for h in [h for h in testcase.houses if h.owner is not None] if h.owner.dead == True]
        if len(owner_dead) > 0:
            print('Something has gone wrong')
            break
    plot_classify(testcase.houses)
    
    df = pd.DataFrame({'classify' : [classify_household(h) for h in testcase.houses if len(h.people)>0], 'size' : [len(h.people) for h in testcase.houses if len(h.people)>0]})
    groups = df.groupby('classify')
    groups.mean()
    
    hist([len(h.people) for h in testcase.houses],range(21))

    
        
        agelist.append(np.mean([x.age for x in testcase.people]))
        below15.append(sum([1.0 for x in testcase.people if x.age<=15])/testcase.population*1.0)
    plt.

def letsget(x):
    out = []
    for i in xrange(10):
        out.append(x)
    return out

