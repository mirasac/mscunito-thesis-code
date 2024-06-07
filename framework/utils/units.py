import pint
import xarray

def to_scalar_quantity(
        source: xarray.DataArray,
        ureg: pint.UnitRegistry = None
    ):
    """Convert `source` as a scalar xarray.DataArray object with units
    to a Quantity object from `ureg`, which is Pint's default if not specified.
    """
    if ureg is None:
        ureg = pint.UnitRegistry()
    _return = None
    if isinstance(source, xarray.DataArray):
        if not "units" in source.attrs:
            _return = source.data
        else:
            _return = ureg.Quantity(source.data, source.attrs["units"])
    return _return

def units(
        value: xarray.DataArray | xarray.Dataset,
        ureg: pint.UnitRegistry = None,
        coords=False,
        func=None
    ):
    """Return a dict with units of `value` as values if available
    in the specified UnitRegistry `ureg` (which default to Pint's).
    The keys are the name of the variables.
    If `coords` is set to `True`, then add also the units of the coordinates.

    Parameters
    ----------
    func
        Function to apply to value to extract its units.
    """
    if ureg is None:
        ureg = pint.UnitRegistry()
    dataarrays = []
    if isinstance(value, xarray.DataArray):
        dataarrays.append(value)
    elif isinstance(value, xarray.Dataset):
        dataarrays.extend(value.data_vars.values())
    if coords:
        dataarrays.extend(value.coords.values())
    print(dataarrays)
    if func is None:
        def _func(source):
            return to_scalar_quantity(source[0], ureg=ureg).units
        func =_func
    return {f"{item.name}": func(item) for item in dataarrays}
