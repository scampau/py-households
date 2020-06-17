"""The __init__.py file for the households package

Imports the dependencies requires, then
the various primary modules and the behavior package.
"""
import numpy as np
import random as rd
import scipy
import networkx as nx
import matplotlib.pyplot as plt
import inspect

print('Importing the households package')
from households.identity import *
import households.kinship
import households.residency
import households.behavior
from households.main import *
import households.narrative

