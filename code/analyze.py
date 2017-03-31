# Analysis and interpretation of results
import numpy as np
import random as rd
import scipy as sp
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import copy as cp

filename = 'simulation_results.csv'
folder = '../results/'
runs = pd.read_csv(folder + filename)

def ecdf(data):
    """
    Get an empirical cumulative distribution.
    """
    data.sort()
    density = [1./len(data)]*len(data)
    cumdensity = np.cumsum(density)
    output =  np.array([data,cumdensity])
    return output.T

# Longevity of household occupation
# Pick which sets you will be contrasting
contrast = [runs['locality'] == 'neolocality', runs['locality']== 'patrilocality']
#Create a data structure to store the results
distribution = []
for i in xrange(len(contrast)):
    distribution.append({ 'finished' : [], 'unfinished' : []})
# For each group:
for c in xrange(len(contrast)):
    group = contrast[c]
    # Select teh relevant files
    # For each file:
    for i in group.index:
        if group[i] == True:
            # open the file that has the classification in it
            data = pd.read_csv(folder+str(runs.ix[i]['id'])+'_house_classify.csv',index_col=0)
            # For every house:
            for h in data.columns[1:]:
                # Begin a counter
                counter = 0
                # For each year:
                for y in data.index:
                    #  if empty and counter 0, pass, otherwise record and reset
                    if data[h][y] == 'empty':
                        if counter == 0:
                            pass
                        else:
                            distribution[c]['finished'].append(counter)
                            counter = 0
                    else:
                        #House is occupied
                        #Add 1
                        counter += 1
                        if y == max(data.index):
                            # if last, add 1 and then add to the list of unfinished runs
                            distribution[c]['unfinished'].append(counter)

#Plot the histogram and kernel for each one of htese in turn
c = 0
plt.hist(distribution[c]['finished'],normed=True,bins=range(0,300,5))
d = cp.copy(distribution[c]['finished'])
kern = sp.stats.gaussian_kde(d)
pdf = kern.pdf(np.unique(d))
plt.plot(np.unique(d),kern(np.unique(d)),'b-')
plt.xlabel('Years')
plt.ylabel('Probability')
plt.title('Patrilocality')

# Plot the kernels together
colors = ['r-','b-']
for c in xrange(len(contrast)):
    #Copy the array
    d = cp.copy(distribution[c]['finished'])
    cdf = ecdf(d)
    kern = sp.stats.gaussian_kde(d)
    pdf = kern.pdf(np.unique(d))
    plt.plot(np.unique(d),kern(np.unique(d)),colors[c])
plt.legend('Neolocality','Patrilocality')

#Write this data
filenames = ['neolocality_lifespan_data','patrilocality_lifespan_data']
for c in xrange(len(contrast)):
    #make each dictionary into a 
    for k in ['finished','unfinished']:
        d = pd.DataFrame(distribution[c][k])
        d.to_csv('../analysis/'+filenames[c]+'_' + str(k) + '.csv',index=False)
    
    
    #
    m = np.mean(d)
    v = np.var(d)
    mode = [x for x in np.unique(d) if kern.pdf(x) == max(pdf)][0]
    alpha = (m**2)/v
    beta = m/v
    g = sp.stats.gamma(alpha,scale=1/beta)
    plt.plot(np.unique(d),g.pdf(np.unique(d)))
    p = sp.stats.gamma.fit(d)
    g = sp.stats.gamma(p[0],loc=p[1],scale=p[2])
    plt.plot(np.unique(d),g.pdf(np.unique(d)))
    
    

# Distribution of family types
arrays = []
typeslist = ['empty','solitary','no-family','nuclear','extended','multiple']
for c in xrange(len(contrast)):
    group = contrast[c]
    # Select teh relevant files
    # For each file:
    collect = []
    for i in group.index:
        if group[i] == True:
            # open the file that has the classification in it
            data = pd.read_csv(folder+str(runs.ix[i]['id'])+'_house_classify.csv',index_col=0)
            # For every house:
            store = []
            for y in data.index:
                counts = [0.]*6
                for h in data.columns[1:]:
                    w = [x for x in xrange(6) if typeslist[x] == data[h][y]][0]
                    counts[w] +=1
                # store this year's counts
                store.append(counts)
            #store this run's counts
            collect.append(store)
    #store this group's counts
    arrays.append(collect)

#Plot an averaged river plot
for c in xrange(len(contrast)):
    averaged = np.zeros((300,6)) #This may need editing depending on the years
    # For each data set
    for x in arrays[c]:
        for y in xrange(np.shape(x)[0]):
            averaged[y] += x[y]
    percents = np.zeros((300,5))
    for y in xrange(np.shape(percents)[0]):
        percents[y] = averaged[y][1:]/sum(averaged[y][1:])
    plt.stackplot(range(300),np.transpose(percents),baseline='zero')
    plt.axis([0,300,0,1]) 
    plt.legend(['solitary','no-family','nuclear','extended','multiple'],loc=0)
    plt.xlabel('Year')
    plt.ylabel('Percent')
    plt.title('Neolocality, family type by year')
            
        
