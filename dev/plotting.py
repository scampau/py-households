# Plot simulation results

## Stack plot of household composition through time given a dictionary of houses

array = []
labels = ['empty','solitary','no-family','nuclear','extended','multiple']
which = lambda x: [i for i in xrange(len(labels)) if labels[i] == x][0]
for y in xrange(testcase.year):
    new = [0.]*6
    for k in houstory.keys():
        w = which(houstory[k]['classify'][y])
        new[w]+=1
    new = [x*1./sum(new[1:]) for x in new[1:]] # here adjusting for empties;
    ## change if you want to incliude them  
    array.append(new)
plt.stackplot(range(testcase.year),np.transpose(array),baseline='zero')
plt.axis([0,300,0,1])