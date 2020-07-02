# Coding style and philosophy #

This document outlines why the code is written the way it is to enable future (consistent) expansion.

[PEP 8](https://www.python.org/dev/peps/pep-0008/ "Python style guide")

[NumPy documentation guide for docstrings](https://numpydoc.readthedocs.io/en/latest/format.html "Numpy docstrings")


## Iterators ##


- i, j, k are reserved for numerical (indexical) iterations, while x, y, z are reserved for object iterations.
	- For example `[i for i in range(10)]` but `[x for x in ['a','b','c']]`
- p, h, and c are often used when iterating through people, houses, and communities, respectively

##Variables and parameters##
- a parameter that needs to be a given class (e.g. Person) should be the lowercase name of that class (e.g. person) with any differentiating criteria appended at the end (e.g. personold, personnew)
- conversely, parameters and attributes should *never* have a name that implies they belong to an existing class (e.g. rule can only be used for an actual behavior.Rule)
