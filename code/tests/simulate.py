# Run simulations that sweep different parameters

# Step 0: Import packages

import numpy as np
import pandas as pd
import random as rd
import scipy as sp
import networkx as nx
import matplotlib.pyplot as plt
import os

import crules as cr
from ABMDemography import *

# Step 1: import empirical data
# Life tables are Coale and Demeny: Male, west 4, female west 2
## These derive from Bagnall and Frier 1994

#Load the male death function (West 4)
maledeath = pd.read_csv('../data/demo/West4Male.csv')
ages = list(maledeath.Age1) + [list(maledeath.Age2)[-1]]
malerates = list(maledeath[maledeath.columns[2]])

#Load the female death function (West 2)
## Note: it is assumed that the male and female death rates are defined for the
## the same age ranges, following Coalse and Demeny
femaledeath = pd.read_csv('../data/demo/West2Female.csv')
femalerates = list(femaledeath[femaledeath.columns[2]])
bagnallfrierdeath = agetable([0,1] + range(5,105,5), male, malerates, female, femalerates)

#Remove old objects
del maledeath, femaledeath

# Create a birthrate agetable, derived from Bagnall and Frier ch. 7, esp. 139
bagnallfrierbirth = agetable([0,12,40,50,100],female,[0,.3,.1,0],male,[0,0,0,0,0])

# Create a marriage agetable, based on Bagnall and Frier, 113-4 (women) and 116 (men) for Roman egypt
bagnallfriermarriage = agetable([0,12,17,100],female,[0,1./7.5,1./7.5],male,[0,0,0.0866])


# Step 2: Define inheritance and fragmentation regimes
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
    if person.sex == male and any([h.owner == person for h in person.comm.houses]):
        #First priority: male children
        inherited = cr.inheritance.inherit_sons(person,True) #what about grandchildren?
        if inherited == False:
            #Second priority: adoption of brothers' younger sons
            inherited = cr.inheritance.inherit_brothers_sons(person)
            if inherited == False:
                #If there is still no heir, for now the ownership defaults
                cr.inheritance.inherit(person,None)       

def inheritance_radical():
    """
    Upon the death of the patriarch, the house is given to someone in this 
    order:
        
    Male children (partible!?)
    Brothers
    Children of brothers (stay where they are
    """
    pass
    
inheritance_options = [inheritance_moderate]

# Define fragmentation regimes

def brother_loses_out_15(house):
    if house.people != [] and house.owner != None:
        cr.fragmentation.brother_loses_out(house,15)
        
fragmentation_options = [brother_loses_out_15,cr.fragmentation.no_fragmentation]

#Define locality regimes
locality_options = [cr.locality.neolocality,cr.locality.patrilocality]

#Define population levels to investigate
population_options = [250,500]

# Define area options
area_options = [750]


# Step 3: set up the data structures to store the data 

#Spreadsheet 1: simulation parameters and the seed, as well as a unique numerical identifier
## Fields should include: identifier, seed, pop, area; 
## names of locality, inheritance, fragmentation, 
## EVENTUALLY: demographic info too
filename = 'simulation_results.csv'
folder = '../results/'

if filename in os.listdir(folder):
    runs = pd.read_csv(folder+filename,index_col = 0)
    i = runs['id'].max()+1
else:
    runs = pd.DataFrame(columns=['id','seed','pop','area','startage','locality','inheritance','fragmentation'])
    i = 0
#dtype = [int,int,int,int,int,str,str,str])
#dtype=[dtype('int64'),dtype('int64'),dtype('int64'),dtype('int64'),dtype('int64'),dtype('O'),dtype('O'),dtype('O')])
#For each model run, store these by 
#Spreadsheet 2: house classification by year
#Spreadsheet 3: house populations by year
#Spreadsheet 4: population histories by year

# Step 4: run the simulation

repeats = 50
seeds = range(0,repeats*500,500)

years = 300
startage = 12

for N in population_options:
    for A in area_options:
        for I in inheritance_options:
            for L in locality_options:
                for F in fragmentation_options:
                    for x in xrange(repeats):
                        seed = seeds[x]
                        this_run = pd.DataFrame([[i,seed,N,A,startage,L.__name__,I.__name__,F.__name__]],columns=['id','seed','pop','area','startage','locality','inheritance','fragmentation'])
                        #Check if this simulation has been run; if so, don't run it again (no point)
                        if any(pd.concat((runs,this_run))[['seed','pop','area','startage','locality','inheritance','fragmentation']].duplicated()) == False:
                            #Set the seed
                            rd.seed(seed)
                            #Create the simulation
                            simulation = community(N,A,startage,bagnallfrierdeath,bagnallfriermarriage,bagnallfrierbirth,L,I,F)
                            #Set up to record the simulation house data
                            houstory = {}
                            for h in simulation.houses:
                                houstory[h] = {'classify' : [],'pop' : []}
                            # Run the simulation across years
                            for y in xrange(years):
                                simulation.progress()
                                for h in simulation.houses:
                                    houstory[h]['classify'].append(cr.kinship.classify_household(h))
                                    houstory[h]['pop'].append(len(h.people))                
                            #Write this simulation to the main log file
                            runs = pd.concat((runs,this_run))
                            runs.to_csv(folder+filename)
                            #Write the other sheets
                            #Sheet 2: house history of classification
                            array_pop = []
                            array_class = []
                            houses = [id(x) for x in houstory.keys()]
                            for y in xrange(years):
                                new_pop = [y]
                                new_class = [y]
                                for x in houstory.keys():
                                    new_pop.append(houstory[x]['pop'][y])
                                    new_class.append(houstory[x]['classify'][y])
                                array_pop.append(new_pop)
                                array_class.append(new_class)
                            classified = pd.DataFrame(array_class,columns=['year']+houses)
                            classified.to_csv(folder+str(i)+'_house_classify.csv')
                            populated = pd.DataFrame(array_pop,columns=['year']+houses)
                            populated.to_csv(folder+str(i)+'_house_pop.csv')
                            # Sheet 4: population histories
                            data = pd.DataFrame({'pop' : simulation.poplist,
                            'area' : simulation.arealist,
                            'year' : range(years+1),
                            'birth': simulation.birthlist,
                            'death': simulation.deathlist,
                            'occupied' : simulation.occupiedlist,
                            'marriages' :simulation.marriedlist})
                            data.to_csv(folder+str(i)+'_history.csv')                 
                            i += 1
