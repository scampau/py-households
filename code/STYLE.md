# Coding style and philosophy #

This document outlines why the code is written the way it is to enable future (consistent) expansion.

PEP 8

NumPy documentation guide for docstrings


## Iterators ##


- i, j, k are reserved for numerical (indexical) iterations, while x, y, z are reserved for object iterations.
	- For example `[i for i in range(10)]` but `[x for x in ['a','b','c']]`

