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