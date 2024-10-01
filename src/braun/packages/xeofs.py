import pathlib
import pickle

import xeofs

def save(model, path):
    """Save the xeofs.EOF model `model` to file `path`."""
    path = pathlib.Path(path).resolve()
    obj = model.serialize()
    with path.open("wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

def load(path):
    """Load the xeofs.EOF model from file `path`."""
    path = pathlib.Path(path).resolve()
    dt = None
    with path.open("rb") as f:
        dt = pickle.load(f)
    return xeofs.single.EOF.deserialize(dt)
