import networkx as nx

g = nx.DiGraph()

g.add_edges_from([(0,1),(2,1),(3,4),(1,4),(3,5),(1,5)])

g.predecessors(1)

g.pred[1]
g.succ[1]

g.pred[1] #get parents
g.succ[1] #get children

def get_siblings(g,n):
    #Get the siblings of a node in a graph
    p = g.pred[n].keys()
    s = g.succ[p[0]].keys()
    return s

def get_relatives_ordered(g,n):
    #Get the closest relatives
    

G = {}
for x in azoria.people:
    G[id(x)] = []
    if x.children != []:
        for i in x.children:
            G[id(x)].append(id(i))