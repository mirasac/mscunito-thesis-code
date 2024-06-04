import pint
import xarray

def to_scalar_quantity(source, ureg=None):
    """Convert to specified target's unit, returns xclim.units.units.Quantity."""
    if ureg is None:
        ureg = pint.UnitRegistry()
    if isinstance(source, xarray.DataArray):
        _return = ureg.Quantity(source.data, source.attrs.get("units", ''))
    return _return
