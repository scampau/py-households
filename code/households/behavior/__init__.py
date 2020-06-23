"""Defines individual- and household-scale demographic behaviors

The behavior package specifies how persons can behave - when they choose to 
leave their original household, how marriage or inheritance affects that 
decision, where they end up living, etc. This module is designed to be expandable,
such that future modules can extend types of behavioral diversity that can be
modeled.
"""

__all__ = ['inheritance','marriage','mobility','conception','transmission']

print('importing behavior')

from .main import Rule
from . import inheritance
from . import marriage
from . import mobility
from . import conception
from . import transmission

#from households import main
