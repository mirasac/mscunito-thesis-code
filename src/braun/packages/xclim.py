import itertools

import numpy
import xarray
import xclim

from braun.utils.generic import product
from braun.utils.units import to_scalar_quantity

_ALLOWED_KINDS = [
    xclim.core.utils.InputKind.QUANTIFIED,
    xclim.core.utils.InputKind.NUMBER
]

PARAMETERS_WITH_UNITS = {"thresh_tasmin", "thresh_tasmax", "thresh"}  # Exploit hash table of sets for quick lookup.

def get_variable_parameters(indicator) -> dict:
    """Return a dict containing the parameters of `indicator`
    which can be varied.
    
    Only some parameters can be varied, they are identified among the properties
    listed at https://github.com/Ouranosinc/xclim/blob/edf1e13b7d47e4ead94506cdbb3bce1f977376f9/xclim/core/utils.py#L523.
    """
    return {f"{key}": p for key, p in indicator.parameters.items() if p.kind in _ALLOWED_KINDS}

def set_variable_parameters(parameters_dict: dict, intervals: dict):
    """Add interval for parameters specified as keyword arguments,
    if they are present in `indicator_dict`, which is updated in place.
     
    Parameter `indicator_dict` must have same structure of the returned
    object of function `get_variable_parameters`.
    """
    for i in parameters_dict:
        if i in intervals:
            parameters_dict[i] = intervals[i]

def print_variable_parameters(indicator):
    print(indicator.identifier)
    print(indicator.abstract)
    d = get_variable_parameters(indicator)
    for p in d:
        print(f"- {p}: {d[p].description}")

def get_combinations(intervals: dict):
    """Return three dictionaries with the name of the indicator as key and
    the value depends on the element. In order, values are: numpy array of
    combinations of parameters, sequence with the names of the parameters,
    tuple with the units of the parameters. The order of values in each
    sequence is important because relates the content of the returned elements
    (e.g. first position in alla returned objects refers to the same parameter).
    """
    dim = {}
    combinations = {}
    units = {}
    for i in intervals:  # For each indicator...
        dim[i] = []
        units[i] = []
        _arg_product = []
        for p in intervals[i]:  # ...take its parameters and for each...
            dim[i].append(p)  # ...store information on its name...
            units[i].append(intervals[i][p].attrs["units"])  # ...and their units...
            _arg_product.append(intervals[i][p].values)  # ...also store the ndarray of values...
        # ...to finally obtain the combinations of parameter values, a custom
        # product function is used to allow an arbitrary number of input arrays.
        combinations[i] = product(*_arg_product)
    return (dim, combinations, units)

# Deprecated.
def get_combinations_q(intervals: dict):
    """This is an alternative implementation with pure Python statements,
    but it is much slower than an implementation with numpy arrays
    (cf. get_combinations). Each combination is a sequence of Quantity objects.
    """
    dim = {}
    combinations = {}
    units = {}
    for i in intervals:  # For each indicator...
        dim[i] = []
        units[i] = []
        _arg_product = []
        for p in intervals[i]:  # ...take each of its parameters...
            dim[i].append(p)  # ...store its name respecting the order...
            units[i].append(p)  # ...and its units for additional info...
            _interval = []  # ...then replace the DataArray with a list of scalars...
            for v in intervals[i][p]:  # ...where each value is a Quantity object...
                _interval.append(to_scalar_quantity(v, xclim.units.units))
            _arg_product.append(_interval)
        # ...and finally obtain the combinations of parameter values, the product
        # function is used to allow an arbitrary number of input arrays.
        combinations[i] = list(itertools.product(*_arg_product))
        # Reduce the number of combinations by removing the ones which are not allowed.
        if "thresh_tasmin" in dim[i] and "thresh_tasmax" in dim[i]:
            i_thresh_tasmin = dim[i].index("thresh_tasmin")
            i_thresh_tasmax = dim[i].index("thresh_tasmax")
            n = len(combinations[i])
            j = 0
            while j < n:  # This loop is a while to allow changing the list while iterating it. 
                if combinations[i][j][i_thresh_tasmin] >= combinations[i][j][i_thresh_tasmax]:
                    combinations[i].pop(j)
                    n = n - 1
                else:
                    j = j + 1
    return (dim, combinations, units)

def prepare_combinations(dim: dict, combinations: dict, units: dict):
    """Remove invalid combinations from `combinations` and
    return a tuple with the resulting dict and
    a dict with same structure but lists instead of numpy arrays and
    with values formatted for xclim.
    """
    combinations_reduced = {}
    combinations_formatted = {}
    for i in combinations:  # Apply to each indicator.
        combinations_formatted[i] = []  # Use lists to allow contents of different type.
        idx_thresh_tasmin = None
        idx_thresh_tasmax = None
        if "thresh_tasmin" in dim[i] and "thresh_tasmax" in dim[i]:
            idx_thresh_tasmin = dim[i].index("thresh_tasmin")
            idx_thresh_tasmax = dim[i].index("thresh_tasmax")
        obj_delete = []
        for j, c in enumerate(combinations[i].tolist()):
            # Remove combinations which are not allowed.
            if (
                idx_thresh_tasmin is not None and idx_thresh_tasmax is not None and
                c[idx_thresh_tasmin] >= c[idx_thresh_tasmax]
            ):
                obj_delete.append(j)
            # Format values as requested by xclim indicators.
            else:
                for k, value in enumerate(c):
                    if dim[i][k] in PARAMETERS_WITH_UNITS:
                        c[k] = f"{value} {units[i][k]}"
                    else:  # Specify other formats.
                        if dim[i][k] == "window":
                            c[k] = int(value)
                combinations_formatted[i].append(c)
        combinations_reduced[i] = numpy.delete(combinations[i], obj_delete, axis=0)
    return combinations_reduced, combinations_formatted

def compute(indicator, parameters: dict, values: dict, **kwargs):
    _da = indicator(**parameters, **kwargs)
    # Can not expand in a single step because
    # non integer scalars are not allowed in expand_dims.
    _da = _da.assign_coords(values)
    _da = _da.expand_dims(tuple(values.keys()))
    if _da.chunks is not None:
        _da = _da.chunk(chunks={"time": -1})
    return _da

def compute_alternative(indicator, parameters: dict, units: dict, **kwargs):
    p = dict(parameters)
    for k in p:
        if k in PARAMETERS_WITH_UNITS:
            # Format requested by xclim.
            p[k] = f"{p[k]} {units[k]}"
        else:
            if k == "window":
                p[k] = int(p[k])
    _da = indicator(**p, **kwargs)
    # Can not expand in a single step because
    # non integer scalars are not allowed in expand_dims.
    _da = _da.assign_coords(parameters)
    _da = _da.expand_dims(tuple(parameters.keys()))
    if _da.chunks is not None:
        _da = _da.chunk(chunks={"time": -1})
    return _da

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
        for pp in p.values():  # MC debug.
            print(pp)  # MC debug.
        print(indicator_kwargs)  # MC debug.
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
