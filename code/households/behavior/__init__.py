"""Defines individual- and household-scale demographic behaviors

The behavior package specifies how persons can behave - when they choose to 
leave their original household, how marriage or inheritance affects that 
decision, where they end up living, etc. This module is designed to be expandable,
such that future modules can extend types of behavioral diversity that can be
modeled.
"""

__all__ = ['inheritance','locality','fragmentation']

print('importing behavior')

from . import inheritance
from . import locality
from . import fragmentation