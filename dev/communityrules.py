###############################################################################


global male, female
male, female = xrange(2)

## Inheritance regimes
### Each of these runs multiple rules
def inheritance_moderate(agent):
    """
    Upon the death of the patriarch, the house is given to someone in this
    order:
        
    Male children in order of age
    Children of brothers not in line for succession (have to move into household)
    
    This stems from the description of the moderate inheritance regime in Asheri
    """
    #The moderate inheritance regime of Asheri 1963
    # Check if patriarch
    if agent.sex == male and any([h.owner == agent for h in agent.comm.houses]):
        #First priority: male children
        inherited = cr.inheritance.inherit_sons(agent,True) #what about grandchildren?
        if inherited == False:
            #Second priority: adoption of brothers' younger sons
            inherited = cr.inheritance.inherit_brothers_sons(agent)
            if inherited == False:
                #If there is still no heir, for now the ownership defaults
                cr.inheritance.inherit(agent,None)                                  
    
    
    
def inheritance_radical():
    """
    Upon the death of the patriarch, the house is given to someone in this 
    order:
        
    Male children (partible!?)
    Brothers
    Children of brothers (stay where they are
    """

