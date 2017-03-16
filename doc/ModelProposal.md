# Model Proposal for the Greek House Inheritance Model

Andrew Cabaniss

* Course ID: CMPLXSYS 530
* Course Title: Computer Modeling of Complex Systems
* Term: Winter, 2017



&nbsp; 

### Goal 
*****
 
This model aims to model the demographic cycle of families in houses for the Mediterranean. The outcomes are the life histories of houses, rather than families.

&nbsp;  
### Justification
****
ABM enables individuals in households to be modeled in explicit detail, which is critical for understanding the changing history of families, the lifecycle of households, and the way this affects the histories of houses.

&nbsp; 
### Main Micro-level Processes and Macro-level Dynamics of Interest
****

Individuals are governed by the biological processes of birth and death, while families and households arise from the interaction of these factors with marriage and inheritance. The distribution of household lifecycles through time can then be compared with the aggregate archaeological record for houses to check coherence with the model.

&nbsp; 


## Model Outline
****
&nbsp; 
### 1) Environment

The environment at this stage of modeling is aspatial. Houses and their component families exist in a generic collection of entities called a __community__. The **community** stores the people and houses, and updates them at each turn. 

The **community** has the following variables:
* houses and people - lists of all house and people objects, respectively.
* area and population - the count of how many houses and people there are at a given moment.
* morrtab, marrtab, birthtab - variables that store **agetables**, a class of object that provides look-up functions for agents based on age and sex.
* deaths, births - how many deaths and births took place each step
* thedead - list of all dead agents for geneaological record keeping
* deathlist, birthlist, poplist, arealist - time series for births, deaths, population, and houses

The **community** has the following methods:
* progress - progress the community one time step. This involves iterating through all agents for the death, marriage, and birth methods each time step. These must be done sequentially in order to prevent mixups.
* get_eligible - returns a list of all people eligible for marriage of a different sex.
* get_kin_network - returns a network of kinship for the community. Required for many inheritance and marriage rules.


_**LS Comments:**: Extremely clear and well thoughtout setup here! Also, I appreciate your commitment to empirical grounding with regard to using age tables._

```python
## The initialization code for the community
class community(object):
    """
    Communities store collections of people and houses.
    
    """
    
    global male, female
    def __init__(self,pop,area,mortab,marrtab,birthtab):
        """
        Initialize the community with initial people and houses, as well as demographic dynamics
        
        Initializing a community takes the following:
            pop: the initial population (should be at least 2x that desired)
            area: the number of houses (for now an integer)
            mortab: the agetable for mortality by sex
            marrtab: the agetable for marriage eligibility by sex
            birthtab: the agetable for birth probability once married by sex (e.g. 0 for males at all ages)
        """
        
        # Create the houses
        self.area = area #The number of houses to create
        self.houses = []
        for i in xrange(area):
            self.houses.append(house(10,self)) #Create each house with a maximum numbe rof people who can reside there
            
        #########################################################
        # LS Comments: Looks like house() is also a class you will be defining? Didn't see it here 
        # in the proposal, but no worries - you've definitely got a lot developed already!
        ##########################################################
        
        
        self.housingcapacity = sum([i.maxpeople for i in self.houses])    
        
        # Generate the population
        self.population = pop #The number of individuals to start in the community
        # populate the community
        self.people = []
        for i in xrange(pop):
            self.people.append(person(rd.choice([male,female]),0,None,None,self)) #Generate a new person with age 0
        
        #########################################################
        # LS Comments: How were you thinking about handling initial house assignment? Maybe there is a provision
        # in the marriage-move that indicates newlyweds can go to a vacant house?
        ##########################################################

        #Define dynamics of demography
        self.mortab = mortab # the death table for the community
        self.marrtab = marrtab #the probability of marriage at a given age by sex
        self.birthtab = birthtab #the probability of a woman giving birth at a given age if married
        
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
        self.arealist.append(self.area)

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
        
        ###LIKE THE DEATH STAR, THIS IS NOT FULLY OPERATIONAL YET
        F = {} #the forward graph, children
        B = {} #the backward graph, parents
        if alive == True:
            for x in self.people:
                B[id(x)] = [[x.father if x.father.dead == False else None], x.mother]
                F[id(x)] = x.children
        else:
            pass
            #for x in self.people + self.thedead:
            
        #########################################################
        # LS Comments: A lot of the 2nd-generation information that is captured by these network is being directly 
        # held in your person objects right now. If you find yourself short on time right now, you might be able to easily
        # get away with only constructing these networks at the end of your simulation for display purposes so long
        # as your rules don't require information beyond immediate generational connections. That presumes that in this 
        # early version, marriage continues ignoring kinship (though you could still condition on not being direct siblings) and  
        # that inheritence rules don't require anything beyond child sex and age. Just a short-term idea. 
        # 
        # Conversely, once you get a more fully developed model, you might consider just letting your (directed) kin 
        # networks store familial relationship information for you instead of the person objects, just to cut down on redundancy and
        # memory requirements. 
        ##########################################################
```

&nbsp; 

### 2) Agents

The main agents of the system are people who live in the community, defined by the **person** class.

A member of the **person** class has the following variables:
* sex - male or female
* age - current age in steps (years)
* mother - a pointer to the agent's mother, else None
* father - a pointer to the agent's father, else None
* comm - a pointer to the agent's community
* house - a pointer to the agent's house, else None
* dead - a boolean for whether the agent is dead and needs to be removed from the community
* married - a pointer to the agent's spouse if there is one, else None
* eligible - a boolean for whether the agent is eligible for marriage
* children - a list of all agents who are the children of this agent, whether alive or dead

A member of the **person** class has the following methods:
* die - check the mortab of the community to see if this agent dies. If so, flag for removal
   * Rules concerning inheritance apply here
* marriage - possible have the agent marry another agent.
  * If the agent is married, this step is skipped
  * If the agent is eligible for marriage, find another eligible agent of the opposite sex and marry them
    * Rules concerning location upon marriage apply at this point
  * If the agent is not eligible for marriage, check the marrtab of the community to see whether the agent might become eligible

 
_**LS Comments:** Looks like "birth" is also in here. You also might think of "Move" as its own method. Or maybe you are handling that at the "House" level? If so, still will require action on the part of the agents._

```python
class person(object):
    """
    A person is an agent with a social structure and kinship.
    
    """
    def __init__(self,sex,age,mother,father,comm,house):
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
        self.house = house #link to their house
        
        self.dead = False
        self.married = None #pointer to who they are married if not None
        self.eligible = False #if eligible for marriage
        self.children = []
        
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
            
    def marriage(self):
        """
        Check whether this agent gets married this timestep.
        
        """
        
        if self.married != None: #if married, don't run this script
            next
        if self.eligible == True: #if this agent is eligible to be married
            candidates = self.comm.get_eligible([male if self.sex == female else female][0])#get the list of eligible candidates for marriage
            ##NOTE: eventually this must be adapted to get those not related to a given person by a certain distance
            
            #########################################################
            # LS Comments: W/o kinship networks, you can get at this in a coarse way by subsetting candidates by those
            # who do not have the same parent or house.
            ##########################################################
            
            if len(candidates) != 0: #if there are any eligible people
                self.married = rd.choice(candidates)
                self.eligible = False
                #Set the marriage conditions of the other person
                self.married.married = self
                self.married.eligible = False
                ##NOTE: Eventually LOCATION SHIFT  must occur here
                
        #########################################################
        # LS Comments: You might be planning on this already, but I would suggest pulling out "Marriage-Move" as its own
        # method and then just calling it here unless the rules for moving via marriage will be very simple
        ##########################################################
        
        else: #if not, check eligibility
            e = self.comm.marrtab.get_rate(self.sex,self.age)
            if e > rd.random(): #If eligibility possible, change staus
                self.eligible = True

        
    def birth(self):
        """
        Check whether this agent gives birth to a new child. If so, create that child.
        
        """
        if self.sex == female and [self.married.dead if self.married != None else True][0] == False: #If married, husband is alive, and self is a woman
            b = self.comm.birthtab.get_rate(self.sex,self.age)
            if b > rd.random(): # if giving birth
                child = person(rd.choice([male,female]),0,self,self.married,self.comm) #create a new child
                self.comm.people.append(child) #add to the community
                self.children.append(child) #store that this is your child
                self.married.children.append(child) #have the husband store that this is their child too

```

&nbsp; 

### 3) Action and Interaction 
 
**_Interaction Topology_**

Agents at present are perfectly mixed and marry at random. Rules concerning movement into and out of houses involve checking the composition of the house in which one currently resides or wishes to reside.
 
**_Action Sequence_**

_What does an agent, cell, etc. do on a given turn? Provide a step-by-step description of what happens on a given turn for each part of your model_

For each person during each turn:

1. There is a chance the person will die. If so, they are removed from the model.
  1. If a man dies and owns a house, his house will change ownership following inheritance rules.
2. If the person is unmarried, they may become eligible to marry, and if so they will marry another eligible person of the opposite sex.
  1. If they do marry, one or both of them will change houses, following locality rules.
3. If a woman is married, there is a chance that she will give birth.
  1. A new agent is created and added to the house

&nbsp; 

_**LS Comments:** Overall, super-solid! I was wondering though, is marriage the only reason why agents move houses? If so, what is your housing-capacity variable doing? Is a move required when it a house goes over capacity? If so, I assume that means the non-owners of the house are the ones who have to move, probably to a vacant house?_

### 4) Model Parameters and Initialization

The main global parameters are the population and the area, or the number of people and the number of houses. The other 'parameters' are more along the lines of rules, such as the inheritance rules, the household fragmentation rules, and the locality rules for newlyweds.

The model will be initialized by generating the correct number of people and houses, starting all of the people at a mix of ages. Over the first hundred or so steps, these people will marry and claim houses, form families and have children, die and pass on property, and get the model to sufficient complexity of the social fabric that observations can be made about the dynamics and distriubtion of houses. The burn-out period is likely to be more than one complete generation, but this will need to be established better once the model has calibrated data.

For each tick of the model (representing the passage of 1 year):
1. Randomize the order of the agents
2. Check whether any of them die; remove them if they do, and run inheritance rules.
3. Check whether the household will fragment because of too many people, too many male household heads, etc.
3. Check whether anyone in each house needs to marry and is eligible. If they marry, locality rules are enacted.
4. If women are married, they may give birth, as determined by a fertility table.
5. Recalculate the statistics on the patterns of life, death, and occupancy.

_**LS Comments:** Haven't seen how you are handling the household fragmentation yet (see other comments) but this still looks good. I'll also take a peek at your ABMDemography.py to see if you've gotten to it over there._

&nbsp; 

### 5) Assessment and Outcome Measures

_What quantitative metrics and/or qualitative features will you use to assess your model outcomes?_
Several different estimates of the distribution of typical family types for the Mediterranean in different periods have been published, which makes classifying households according to the Cambridge Group typology useful and needed to check comparability between the model and historical data sets. Measures of household size, household longevity, and house occupancy will be used in examining differences in the effects of inheritance laws, locality rules, and patterns of household fragmentation to understand what correlates might exist in the historical and archaeological record.

_**LS Comments:** Great!_

&nbsp; 

### 6) Parameter Sweep

The main parameters to sweep through are fundamentally the combinations of different rules of inheritance, matrimonial locality, and household fragmentation. Since these are sets of discrete options, the goal will be to check each combination of two or three options for each (patrilocal vs. neolocal, no fragmentation vs. fragmentation for younger brothers, passing to oldest son vs. splitting between sons, etc.) In addition to these, the model will also sweep through different (small) population sizes and different housing stocks, as limited by the minimum requirements of the model.



N. B. All code is available in the /dev/ABMDemography.py script.


_**LS Comments:** Fantastic job!!! You've done a lot of work here, and I think you are definitely on track for a really interesting and potentially, quite compelling model. There are many moving parts here, and for the purposes of getting something that runs and is producing some initial results by the end of the semester, I am going to encourage you to simplify and temporarily "punt"/oversimplify  any of those portions you can easily do so if you find yourself stressed on time._

