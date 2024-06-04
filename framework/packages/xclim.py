import itertools

import xarray
import xclim

from framework.utils.units import to_scalar_quantity

_ALLOWED_KINDS = [
    xclim.core.utils.InputKind.QUANTIFIED,
    xclim.core.utils.InputKind.NUMBER
]

def get_variable_parameters(indicator) -> dict:
    """Return a dict containing the parameters of `indicator`
    which can be varied.
    
    Only some parameters can be varied, they are identified among the properties
    listed at https://github.com/Ouranosinc/xclim/blob/edf1e13b7d47e4ead94506cdbb3bce1f977376f9/xclim/core/utils.py#L523.
    """
    return {f"{key}": p for key, p in indicator._all_parameters.items() if p.kind in _ALLOWED_KINDS}

def compute_variations(indicator, variations, **indicator_kwargs) -> xarray.Dataset:
    """Apply compute function of `indicator` using the values in dictionary
    `variations` specified for each varied parameter.
    
    Parameters
    ----------
    **indicator_kwargs
        Keyword arguments to pass to the indicator.
    
    Return
    ------
    xarray.DataArray object containing the varied parameters
    as additional dimensions and their values as coordinates.
    A single data variable is set corresponding to the results of the indicator,
    assigned to the new coordinates which where used as parameters.
    Its name is the name of the indicator identifier.
    """
    # Remove varied parameters from kwargs to avoid problems during unpacking.
    dims_add = tuple(variations.keys())
    for key in dims_add:
        indicator_kwargs.pop(key, None)
    list_res = []
    # Starting with Python 3.7 dict preserves the order of insertion.
    for item in itertools.product(*variations.values()):
        p = {f"{da.name}": to_scalar_quantity(da, xclim.units.units) for da in item}
        res = indicator(**p, **indicator_kwargs)
        c = dict(zip(dims_add, item))
        # Can not expand in a single step because
        # scalar DataArray objects are not allowed in expand_dims.
        res = res.assign_coords(c)
        res = res.expand_dims(dims_add)
        list_res.append(res)
    return xarray.combine_by_coords(
        data_objects=list_res,
        combine_attrs="drop_conflicts"
    )
