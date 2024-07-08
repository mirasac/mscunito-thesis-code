import pint
import xarray

def to_scalar_quantity(
        source: xarray.DataArray,
        ureg: pint.UnitRegistry = None
    ):
    """Convert `source` as a scalar xarray.DataArray object with units
    to a Quantity object from `ureg`, which defaults to Pint's registry.
    """
    if not isinstance(source, xarray.DataArray):
        TypeError(source)
    if ureg is None:
        ureg = pint.UnitRegistry()
    elif not isinstance(ureg, pint.UnitRegistry):
        TypeError(ureg)
    magnitude = source.values
    units = source.attrs.get("units", "")
    return ureg.Quantity(magnitude, units)
