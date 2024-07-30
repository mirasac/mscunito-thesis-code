import numpy

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
