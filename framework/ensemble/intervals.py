"""
Define classes and utilities for intervals management.

Since mathematical operations on continuous numbers performed by computers are intrinsically discretised, intervals are defined as xarray.DataArray objects.

An inspiration can be https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Interval.html#pandas-interval.
"""

import numpy
import pandas
import pint
import xarray


_MAX_LENGTH = 100

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
    
    def to_numpy(self, **kwargs):
        return numpy.linspace(
            start=self.left,
            stop=self.right,
            endpoint=True,
            **kwargs
        )
    
    def to_dataarray(self, **kwargs):
        numpy_kwargs = {}
        for kw in ("num",):
            if kw in kwargs:
                numpy_kwargs[kw] = kwargs.pop(kw)
        return xarray.DataArray(data=self.to_numpy(**numpy_kwargs), **kwargs)

class IntervalInteger(IntervalNumeric):
    def __init__(self, left, right, name=None):
        self.n = right - left + 1
        super().__init__(left, right, name)
    
    def __str__(self):
        if self.n == 2:
            _return = f"{{{self.left}, {self.right}}}"
        elif self.n <= _MAX_LENGTH:
            inner = ", ".join(str(i) for i in range(self.left, self.right + 1))
            _return = f"{{{inner}}}"
        else:
            _return = f"{{{self.left}, ..., {self.right}}}"
        return _return
    
    def to_numpy(self, **kwargs):
        return numpy.arange(
            start=self.left,
            stop=self.right + 1
        )

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
    
    def to_dataarray(self, **kwargs):
        da = super().to_dataarray(**kwargs)
        da.attrs["units"] = str(self.units)
        return da

class CategoricalInterval:
    pass
