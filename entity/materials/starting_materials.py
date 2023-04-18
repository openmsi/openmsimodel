'''Classes for starting materials.'''

from entity.base import Material

__all__ = ['PurchasedMaterial', 'ElementalMaterial', 'AtmosphericMaterial']

class PurchasedMaterial(Material):
    '''Class for materials that have been purchased from a supplier.'''


class ElementalMaterial(PurchasedMaterial):
    '''Class for pure elements that have been purchased from a supplier.'''


class AtmosphericMaterial(Material):
    '''Class for materials present due to a particular atmosphere.'''
