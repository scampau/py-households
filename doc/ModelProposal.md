# Model Proposal for the Greek House Inheritance Model

Andrew Cabaniss

* Course ID: CMPLXSYS 530
* Course Title: Computer Modeling of Complex Systems
* Term: Winter, 2017



&nbsp; 

### Goal 
*****
 
This model aims to model the demographic cycle of families in houses for the Mediterranean. The outcomes are the life histories of houses, rather than families.

&nbsp;  
### Justification
****
ABM enables individuals in households to be modeled in explicit detail, which is critical for understanding the changing history of families, the lifecycle of households, and the way this affects the histories of houses.

&nbsp; 
### Main Micro-level Processes and Macro-level Dynamics of Interest
****

Individuals are governed by the biological processes of birth and death, while families and households arise from the interaction of these factors with marriage and inheritance. The distribution of household lifecycles through time can then be compared with the aggregate archaeological record for houses to check coherence with the model.

&nbsp; 


## Model Outline
****
&nbsp; 
### 1) Environment
_Description of the environment in your model. Things to specify *if they apply*:_

* _Boundary conditions (e.g. wrapping, infinite, etc.)_
* _Dimensionality (e.g. 1D, 2D, etc.)_
* _List of environment-owned variables (e.g. resources, states, roughness)_
* _List of environment-owned methods/procedures (e.g. resource production, state change, etc.)_

The environment at this stage of modeling is aspatial. Houses and their component families exist in a generic collection of entities called a __community__. The **community** stores the people and houses, and updates them at each turn. 

The **community** has the following variables:
* houses and people - lists of all house and people objects, respectively.
* area and population - the count of how many houses and people there are at a given moment.
* morrtab, marrtab, birthtab - variables that store **agetables**, a class of object that provides look-up functions for agents based on age and sex.
* deaths, births - how many deaths and births took place each step
* thedead - list of all dead agents for geneaological record keeping
* deathlist, birthlist, poplist, arealist - time series for births, deaths, population, and houses

The **community** has the following methods:
* progress - progress the community one time step. This involves iterating through all agents for the death, marriage, and birth methods each time step. These must be done sequentially in order to prevent mixups.
* get_eligible - returns a list of all people eligible for marriage of a different sex.
* get_kin_network - returns a network of kinship for the community. Required for many inheritance and marriage rules.

```python
# Include first pass of the code you are thinking of using to construct your environment
# This may be a set of "patches-own" variables and a command in the "setup" procedure, a list, an array, or Class constructor
# Feel free to include any patch methods/procedures you have. Filling in with pseudocode is ok! 
# NOTE: If using Netlogo, remove "python" from the markdown at the top of this section to get a generic code block
```

&nbsp; 

### 2) Agents
 
 _Description of the "agents" in the system. Things to specify *if they apply*:_
 
* _List of agent-owned variables (e.g. age, heading, ID, etc.)_
* _List of agent-owned methods/procedures (e.g. move, consume, reproduce, die, etc.)_

The main agents of the system are people who live in the community, defined by the **person** class.

A member of the **person** class has the following variables:
* sex - male or female
* age - current age in steps (years)
* mother - a pointer to the agent's mother, else None
* father - a pointer to the agent's father, else None
* comm - a pointer to the agent's community
* house - a pointer to the agent's house, else None
* dead - a boolean for whether the agent is dead and needs to be removed from the community
* married - a pointer to the agent's spouse if there is one, else None
* eligible - a boolean for whether the agent is eligible for marriage
* children - a list of all agents who are the children of this agent, whether alive or dead

A member of the **person** class has the following methods:
* die - check the mortab of the community to see if this agent dies. If so, flag for removal
   * Rules concerning inheritance apply here
* marriage - possible have the agent marry another agent.
  * If the agent is married, this step is skipped
  * If the agent is eligible for marriage, find another eligible agent of the opposite sex and marry them
    * Rules concerning location upon marriage apply at this point
  * If the agent is not eligible for marriage, check the marrtab of the community to see whether the agent might become eligible

 


```python
# Include first pass of the code you are thinking of using to construct your agents
# This may be a set of "turtle-own" variables and a command in the "setup" procedure, a list, an array, or Class constructor
# Feel free to include any agent methods/procedures you have so far. Filling in with pseudocode is ok! 
# NOTE: If using Netlogo, remove "python" from the markdown at the top of this section to get a generic code block
```

&nbsp; 

### 3) Action and Interaction 
 
**_Interaction Topology_**

Agents at present are perfectly mixed and marry at random. Rules concerning movement into and out of houses involve checking the composition of the house in which one currently resides or wishes to reside.
 
**_Action Sequence_**

_What does an agent, cell, etc. do on a given turn? Provide a step-by-step description of what happens on a given turn for each part of your model_

For each person during each turn:

1. There is a chance the person will die. If so, they are removed from the model.
  1. If a man dies and owns a house, his house will change ownership following inheritance rules.
2. If the person is unmarried, they may become eligible to marry, and if so they will marry another eligible person of the opposite sex.
  1. If they do marry, one or both of them will change houses, following locality rules.
3. If a woman is married, there is a chance that she will give birth.
  1. A new agent is created and added to the house

&nbsp; 
### 4) Model Parameters and Initialization

The main global parameters are the population and the area, or the number of people and the number of houses. The other ``parameters'' are more along the lines of rules, such as the inheritance rules, the household fragmentation rules, and the locality rules for newlyweds.

The model will be initialized by generating the correct number of people and houses, starting all of the people at a mix of ages. Over the first hundred or so steps, these people will marry and claim houses, form families and have children, die and pass on property, and get the model to sufficient complexity of the social fabric that observations can be made about the dynamics and distriubtion of houses. The burn-out period is likely to be more than one complete generation, but this will need to be established better once the model has calibrated data.

For each tick of the model (representing the passage of 1 year):
1. Randomize the order of the agents
2. Check whether any of them die; remove them if they do, and run inheritance rules.
3. Check whether the household will fragment because of too many people, too many male household heads, etc.
3. Check whether anyone in each house needs to marry and is eligible. If they marry, locality rules are enacted.
4. If women are married, they may give birth, as determined by a fertility table.
5. Recalculate the statistics on the patterns of life, death, and occupancy.


&nbsp; 

### 5) Assessment and Outcome Measures

_What quantitative metrics and/or qualitative features will you use to assess your model outcomes?_
Several different estimates of the distribution of typical family types for the Mediterranean in different periods have been published, which makes classifying households according to the Cambridge Group typology useful and needed to check comparability between the model and historical data sets. Measures of household size, household longevity, and house occupancy will be used in examining differences in the effects of inheritance laws, locality rules, and patterns of household fragmentation to understand what correlates might exist in the historical and archaeological record.

&nbsp; 

### 6) Parameter Sweep

The main parameters to sweep through are fundamentally the combinations of different rules of inheritance, matrimonial locality, and household fragmentation. Since these are sets of discrete options, the goal will be to check each combination of two or three options for each (patrilocal vs. neolocal, no fragmentation vs. fragmentation for younger brothers, passing to oldest son vs. splitting between sons, etc.) In addition to these, the model will also sweep through different (small) population sizes and different housing stocks, as limited by the minimum requirements of the model.

