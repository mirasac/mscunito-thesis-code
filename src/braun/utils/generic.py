import numpy
import xarray

def product(*arrays):
    """Fast implementation to evaluate cartesian product of an arbitrary number
    of arrays with different sizes, from https://stackoverflow.com/a/11146645.
    """
    la = len(arrays)
    dtype = numpy.result_type(*arrays)
    arr = numpy.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(numpy.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la)

def open_dataset_NaT(filename_or_obj, other=None, drop=None, **kwargs):
    """Beware that xarray reads integer numbers in NetCDF files as
    time intervals by default. This means that
    the numerical representation of NaT values is loaded, instead of
    setting NaN. This further operation is done manually by exploiting
    the fact that only some indicators result in integer values
    which are always non negative.
    
    Parameters `other` and `drop` are optional arguments of
    method `Dataset.where`, the others are arguments for
    method `xarray.open_dataset`.
    """
    kwargs.pop("decode_timedelta", None)
    where_kwargs = {}
    if other is not None:
            where_kwargs["other"] = other
    if drop is not None:
            where_kwargs["drop"] = drop
    ds = xarray.open_dataset(filename_or_obj, decode_timedelta=False, **kwargs)
    ds = ds.where((ds >= 0), **where_kwargs)
    return ds

def load_dataset_NaT(filename_or_obj, other=None, drop=None, **kwargs):
    """Load dataset in memory and close file. All parameters are passed to
    `open_dataset_NaT`, analogous to `xarray.load_dataset`.
    """
    kwargs.pop("decode_timedelta", None)
    where_kwargs = {}
    if other is not None:
            where_kwargs["other"] = other
    if drop is not None:
            where_kwargs["drop"] = drop
    ds = xarray.load_dataset(filename_or_obj, decode_timedelta=False, **kwargs)
    ds = ds.where((ds >= 0), **where_kwargs)
    return ds

def rename_coords(ds, prefix="", sep=""):
    """Rename all coordinates of `ds` by prefixing `prefix` to
    the original name, separated by `sep`.
    """
    name_dict = dict.fromkeys(ds.coords)
    for k in name_dict.keys():
        name_dict[k] = f"{prefix}{sep}{k}"
    return ds.rename(name_dict)

def set_quantile_dims(ds):
    """Set coordinates for quantiles, i.e. ending with _q, as dimensions.
    This works only if the swapped coordinates have identical dimension.
    """
    dims_dict = {}
    for k in ds.sizes.keys():
        new_dim = f"{k}_q"
        if new_dim in ds.coords:
            dims_dict[k] = new_dim
    return ds.swap_dims(dims_dict=dims_dict)
