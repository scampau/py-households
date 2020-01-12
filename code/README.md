# Code

Python 2 code implementing the ABM. Part of [**house_inheritance**](../README.md)

----------


ABMDemography and crules provide the actual agent classes for the ABM and a host of demographic and social organization functions, respectively, that enable models to be systematically run (and replicated).

simulate.py runs a basic parameter sweep across different types of behaviors (inheritance regimes, locality, fragmentation rules.)

analyze.py provides some support for handling the data, importing it according to groups (such as fragmentation rules) and then checking various household metrics (longevity of occupation of houses, distribution of family type.)
