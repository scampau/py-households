# To-do list for feature development, addition, and expansion #

This is now slowly being turned into issues in the github to make this more transparent and easier for future collaborators to join. an X in front of an issue means it has been moved to the issue board.

----------

**Short-term**

- X Eliminate duplicate names. 
	- some terms (house, person) are used both as class names and as variables. Go through and update teh nomenclature such that classes are always capitalized, and variable names follow numpy and python conventions.
- X Classes need to be defined that create a unified class for inheritance, locality, and fragmentation rules.
- X Birth rules need to allow uneven sex ratios.
- X Value checks need to make sure that agetables and different rules are used where they need to be.
	- The class system will help with this.
- X Add Du and Kamakura 2006 as well as other household type definitions to the residency module.
	- Expand the module to become a subpackage with different definitions.
- X Let rules not be a community property, but instead part of individuals.
	- Inheritance, locality, fragmentation (And later other rules) need to be conducted by individuals, and be inherited or learned, with those methods of inheritance/learning also definable (and inherited/learned themselves.) 


**Medium-term**

- Once developed, a set of classes and rules need to be created for remarriage, incest prohibitions, divorce.
	- Allow divorce and different causes thereof, as well as different settlement options.
- Matrilineal inheritance.
- Houses need to be able to be variable, expanded, etc.
	- A build function for houses that creates an owner and moves in a family
	- An expansion function that increases the size of the house.
- Non-kin and enslaved/otherwise dependent residents.
	- Also renters/lodgers
- Add household classification options for non-coresidential families, e.g. worker migration.
- Make a **world** class that will hold multiple communities and allow the simulation to include multiple communities.
	- Make it easy to have a single community as well, just in case others want to allow communities in their own way.


**Long-term**

- Multiple/partitive ownership of buildings? Ownership vs. residency problem.
	- Also ownership of multiple buildings.
- Allow polygamy, and consequently allow alternative definition of a "nuclear" family and what this means for fragmentation.