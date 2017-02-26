import numpy as np
import random as rd
import scipy as sp
import networkx as nx

rd.seed()

male, female = xrange(2)

class community(object):
    """
    Communities store collections of people (for now)
    
    """
    global male, female
    def __init__(self,pop,mortab,marrtab,birthtab):
        self.population = pop
        #populate the community
        self.people = []
        for i in xrange(pop):
            self.people.append(person(rd.choice([male,female]),0,None,None,self))
            
        #define dynamics
        self.mortab = mortab # the death table for the community
        self.marrtab = marrtab #the probability of marriage at a given age by sex
        self.birthtab = birthtab #the probability of a woman giving birth at a given age if married
        #define statistics
        self.deaths = 0
        self.births = 0        
        #define history
        self.thedead = [] #store the list of dead agents
        self.deathlist = [self.deaths]
        self.birthlist = [self.births]
        self.poplist = [self.population]

    def progress(self):
        """
        Progress the community 1 year. The order of steps is:
            Death
            Marriage
            Birth
        """
        #Step 1: randomize population order and reset statistics
        rd.shuffle(self.people)
        self.deaths = 0
        self.births = 0
        #Step 2: iterate through each person for death, marriage, and birth
        for x in self.people:
            x.die()
        remove = [i for i in xrange(len(self.people)) if self.people[i].dead == True]
        remove.reverse()
        for i in remove:
            self.thedead.append(self.people.pop(i))
            self.deaths += 1
        for x in self.people:
            x.marriage()
        for x in self.people:
            x.birth()
        #Recalculate statistics
        self.population = len(self.people)
        self.births = len([1 for x in self.people if x.age == 0])
        self.deathlist.append(self.deaths)
        self.birthlist.append(self.births)
        self.poplist.append(self.population)

    def get_eligible(self,sex):
        """
        Get a list of all living people eligible for marriage of a given sex
        """
        candidates = []
        for x in self.people:
            if x.sex == sex:
                if x.eligible == True:
                    candidates.append(x)
        return candidates                    
                
    def get_kin_network(self,alive = True):
        """
        Get the network of kinship for the community as a dict.
        alive - Return the full graph (false) or just the graph of those who are alive (True)
        """
        ###THIS IS NOT OPERATIONAL YET
        F = {} #the forward graph
        B = {} #the backward graph
        if alive == True:
            for x in self.people:
                B[id(x)] = [[x.father if x.father.dead == False else None], x.mother]
                F[id(x)] = x.children
        else:
            pass
            #for x in self.people + self.thedead:


class person(object):
    def __init__(self,sex,age,mother,father,comm):
        """
        Create a new person in the community.
        Sex, age - sex and age at creation of the person (e.g. birth)
        mother, father - references to the person object of the mother and father, else None
        comm - reference to the community the person belongs to.
        """
        self.sex = sex
        self.age = age
        self.mother = mother
        self.father = father
        self.comm = comm #link to the community
        
        self.dead = False
        self.married = None #pointer to who they are married if not None
        self.eligible = False #if eligible for marriage
        self.children = []
    def die(self):
        #figure out if this person dies
        r = self.comm.mortab.get_rate(self.sex,self.age)
        if r <= rd.random(): #stay alive
            self.age += 1
        else: #if this person died this year, toggle them to be removed from the community
            self.dead = True
    def marriage(self):
        """
        Check whether this agent gets married this timestep.
        """
        if self.married != None: #if married, don't run this script
            next
        if self.eligible == True: #if this agent is eligible to be married
            candidates = self.comm.get_eligible([male if self.sex == female else female][0])#get the list of eligible candidates for marriage
            ##NOTE: eventually this must be adapted to get those not related to a given person by a certain distance
            if len(candidates) != 0: #if there are any eligible people
                self.married = rd.choice(candidates)
                self.eligible = False
                #Set the marriage conditions of the other person
                self.married.married = self
                self.married.eligible = False
                ##NOTE: Eventually LOCATION SHIFT AND DOWRY must occur here
        else: #if not, check eligibility
            e = self.comm.marrtab.get_rate(self.sex,self.age)
            if e > rd.random(): #If eligibility possible, change staus
                self.eligible = True

        
    def birth(self):
        """
        Check whether this agent gives birth to a new child. If so, create that child
        """
        if self.sex == female and [self.married.dead if self.married != None else True][0] == False: #If married, husband is alive, and self is a woman
            b = self.comm.birthtab.get_rate(self.sex,self.age)
            if b > rd.random(): # if giving birth
                child = person(rd.choice([male,female]),0,self,self.married,self.comm) #create a new child
                self.comm.people.append(child) #add to the community
                self.children.append(child) #store that this is your child
    
        

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
        i = [i for i in xrange(len(self.ages)-1) if age>=self.ages[i] and age<self.ages[i+1]][0]
        if sex == self.sex1:
            return self.rates1[i]
        else:
            return self.rates2[i]


##Example code
if __name__ == '__main__':
    west2male = agetable([0,1] + range(5,105,5), male, [.38386, .065137, .012644, .009011, .012223, .017511, .019716, .22914, .026903, .03474, .037308, .046951, .056462, .76796, .101664, .139988, .202545, .262221, .361406, .483888, 1], female, [.38386, .065137, .012644, .009011, .012223, .017511, .019716, .22914, .026903, .03474, .037308, .046951, .056462, .76796, .101664, .139988, .202545, .262221, .361406, .483888, 1])
    examplebirth = agetable([0,15,50,100],female,[0,.33,0],male,[0,0,0])
    examplemarriage = agetable([0,15,20,100],female,[0,.5,.5],male,[0,0,.5])
    azoria = community(500,west2male,examplemarriage,examplebirth)
    
    agelist = [np.mean([x.age for x in azoria.people])]
    below15 = [sum([1.0 for x in azoria.people if x.age<=15])/azoria.population*1.0]
    for i in xrange(500):
        azoria.progress()
        agelist.append(np.mean([x.age for x in azoria.people]))
        below15.append(sum([1.0 for x in azoria.people if x.age<=15])/azoria.population*1.0)
        
    plot(below15)
    plot(azoria.poplist,'g-',azoria.birthlist,'b-',azoria.deathlist,'r-')

G = {}
for x in azoria.people:
    G[id(x)] = []
    if x.children != []:
        for i in x.children:
            G[id(x)].append(id(i))

