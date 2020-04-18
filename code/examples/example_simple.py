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


#A fake run with simple data:
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
#Let's check in again on each of the children
for x in children[1:]:
    print('One of the original children:')
    print(households.narrative.biography(x))
    print(x.sex.possessive + ' household:')
    print(households.narrative.census(x.myhouse))
    for y in x.myhouse.people:
        print(households.narrative.biography(y))
    print(' ')
    
    
plt.hist([x.age for x in example.people])
plt.plot(range(example.year+1),example.poplist)
for h in example.houses:
    print(households.narrative.census(h))
    
for x in example.people:
    print(households.narrative.biography(x))