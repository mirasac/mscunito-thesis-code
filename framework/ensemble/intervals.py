"""
Define classes and utilities for intervals management.

Since mathematical operations on continuous numbers performed by computers are intrinsically discretised, intervals are defined as xarray.DataArray objects.

An inspiration can be https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Interval.html#pandas-interval.
"""

import numpy
import pandas
import pint
import xarray


class IntervalAbstract():
    """Base class to expose generic methods on intervals."""
    def __init__(self, left, right, name=None):
        self.left = left
        self.right = right
        self.name = name

class IntervalNumeric(IntervalAbstract):
    """Implementation of a numeric interval, extremes are always included."""
    
    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError

    def __str__(self):
        return f"[{self.left}, {self.right}]"
    
    def to_numpy(self, num):
        return numpy.linspace(
            start=self.left,
            stop=self.right,
            num=num,
            endpoint=True
        )
    
    def to_dataarray(self, num, **kwargs):
        return xarray.DataArray(data=self.to_numpy(num), **kwargs)

class IntervalQuantity(IntervalNumeric):
    """
    Create numeric interval with units which can be converted to xarray.DataArray.
    
    The information on units is persisted and is collected from the left parameter. If units are different but compatible, they are both converted to the base units.
    """

    def __init__(
        self,
        left: pint.Quantity,
        right: pint.Quantity,
        name=None
    ):
        if left._REGISTRY != right._REGISTRY:
            raise pint.PintError("Quantities in the arguments are defined with different Pint registries.")
        else:
            self._REGISTRY = left._REGISTRY
        if not right.is_compatible_with(left):
            raise pint.DimensionalityError(right.units, left.units)
        self.units = left.units
        if right.units != self.units:
            left = left.to_base_units()
            self.units = left.units
            right = right.to(self.units)
        super().__init__(left.magnitude, right.magnitude, name)

    def __str__(self):
        left = self._REGISTRY.Quantity(value=self.left, units=self.units)
        right = self._REGISTRY.Quantity(value=self.right, units=self.units)
        return f"[{left}, {right}]"
    
    def to_dataarray(self, num, **kwargs):
        da = super().to_dataarray(num, **kwargs)
        da.attrs["units"] = str(self.units)
        return da

class CategoricalInterval:
    pass
