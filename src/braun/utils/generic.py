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

def open_dataset_NaT(filename_or_obj, **kwargs):
        """Beware that xarray reads integer numbers in NetCDF files as
        time intervals by default. This means that
        the numerical representation of NaT values is loaded, instead of
        setting NaN. This further operation is done manually by exploiting
        the fact that only some indicators result in integer values
        which are always non negative.
        """
        kwargs.pop("decode_timedelta", None)
        ds = xarray.open_dataset(filename_or_obj, decode_timedelta=False, **kwargs)
        ds = ds.where((ds >= 0))
        return ds
