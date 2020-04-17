"""The __init__.py file for the households package

Imports the dependencies requires, then
the kinship module and the behavior package.
"""
import numpy as np
import random as rd
import scipy
import networkx as nx
import matplotlib.pyplot as plt

print('Importing the households package')
import households.kinship
import households.residency
import households.behavior
from households.main import *
import households.narrative

