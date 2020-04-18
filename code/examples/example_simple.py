# -*- coding: utf-8 -*-
"""Example script for using households.
Created on Tue Apr  7 22:26:25 2020

@author: acabaniss




"""
#Import the households package
import numpy as np
import pandas
import os
import matplotlib.pyplot as plt
#os.chdir('..')
import households


male, female = (households.male,households.female)


#A fake run:
birth = households.AgeTable([0,16,40,100],male,[0,0,0],female,[0,.1,0])
marr = households.AgeTable([0,16,100],male,[0,.8],female,[0,.8])
death = households.AgeTable([0,5,40,100],male,[0,0,1],female,[0,0,1])

def sons_or_none(person):
    result = households.behavior.inheritance.inherit_sons(person,False)
    if result == False:
        households.behavior.inheritance.inherit(person,None)  

def neolocality_husband_owner(husband,wife):
    households.behavior.locality.neolocality(husband,wife,male)

#Run a simple, single example for 25 years
households.rd.seed(505401)
example = households.Community(pop=20,area = 20,startage = 15,mortab = death, marrtab = marr, birthtab = birth, locality = neolocality_husband_owner, inheritance = sons_or_none, fragmentation = households.behavior.fragmentation.no_fragmentation)

while example.year < 25:
    example.progress()

#Let's look at one family
h = [x for x in example.houses if len(x.people) >2][0]
for x in h.people:
    print(households.narrative.biography(x)) 
print(households.narrative.census(h))
print(' ')
#What about the eldest?
children = households.kinship.get_children(h.people[0],h.people[0].mycomm.families)
print(households.narrative.biography(children[0]))
print(households.narrative.biography(children[0].married_to)) #Charlotte's husband
 ## is fromt he first generation, and as such she will soon be a widowed mother

#Now let's run another 25 years
while example.year < 50:
    example.progress()
    
#Let's check in again on each of the children
for x in children:
    print('One of the original children:')
    print(households.narrative.biography(x))
    print(x.sex.possessive + ' household:')
    print(households.narrative.census(x.myhouse))
    for y in x.myhouse.people:
        print(households.narrative.biography(y))
    print(' ')

#And now let's run another 25 years
while example.year < 75:
    example.progress()

#Let's see where the children are now
for x in [maeve, buttercup, robert]:
    print(households.narrative.biography(x) + ' who lives in ' +  households.narrative.census(x.myhouse))

plt.hist([x.age for x in example.people])
plt.plot(range(example.year+1),example.poplist)
[census(x) for x in example.houses]
[biography(x) for x in example.houses[1].people]










###REALISTIC RUNS
#Life tables are Coale and Demeny: Male, west 4, female west 2, .2% annual increase. See Bagnall and frier
maledeath = pandas.read_csv('../data/demo/West4Male.csv')
ages = list(maledeath.Age1) + [list(maledeath.Age2)[-1]]
malerates = list(maledeath[maledeath.columns[2]])
femaledeath = pandas.read_csv('../data/demo/West2Female.csv')
femalerates = list(femaledeath[femaledeath.columns[2]])
age_list = list([0,1]+[x for x in range(5,105,5)])
bagnallfrier = households.AgeTable(ages = age_list , sex1 = male, rates1 = malerates, sex2 = female, rates2 = femalerates)
del maledeath, femaledeath

examplebirth = households.AgeTable([0,12,40,50,100],female,[0,.3,.1,0],male,[0,0,0,0,0])

examplemarriage = households.AgeTable([0,12,17,100],female,[0,1./7.5,1./7.5],male,[0,0,0.0866]) #These values based on Bagnall and Frier, 113-4 (women) and 116 (men) for Roman egypt

def inheritance_moderate(person):
    """
    Upon the death of the patriarch, the house is given to someone in this
    order:
        
    Male children in order of age
    Children of brothers not in line for succession (have to move into household)
    
    This stems from the description of the moderate inheritance regime in Asheri
    """
    #The moderate inheritance regime of Asheri 1963
    # Check if patriarch
    if person.sex == male and any([h.owner == person for h in person.mycomm.houses]):
        #First priority: male children
        inherited = households.behavior.inheritance.inherit_sons(person,True) #what about grandchildren?
        if inherited == False:
            #Second priority: adoption of brothers' younger sons
            inherited = households.behavior.inheritance.inherit_brothers_sons(person)
            if inherited == False:
                #If there is still no heir, for now the ownership defaults
                households.behavior.inheritance.inherit(person,None)    
                
def brother_loses_out_15(house):
    """Fragmentation rule with age of majority 15.
    
    """
    if house.people != [] and house.owner != None:
        households.behavior.fragmentation.brother_loses_out(house,15)
            
#An example of a single realistic run
testcase = households.Community(pop = 500,area = 500,startage = 12, mortab = bagnallfrier,marrtab = examplemarriage,birthtab = examplebirth,locality = households.behavior.locality.patrilocality,inheritance =  inheritance_moderate,fragmentation = brother_loses_out_15)
houstory = {}
for h in testcase.houses:
    houstory[h] = {'classify' : [],'pop' : []}
for i in xrange(200):
    testcase.progress()
    for h in testcase.houses:
        houstory[h]['classify'].append(residency.classify_household(h))
        houstory[h]['pop'].append(len(h.people))
