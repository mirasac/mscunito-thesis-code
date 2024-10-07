# mscunito-thesis-code

Sources for thesis code.

Source code include a Python package with utilities for the analysis performed in the thesis.
The working name of the package is `braun`. It is short and not present in PyPI, just for convenience.

## Versioning

[SemVer 2.0.0](https://semver.org/spec/v2.0.0.html) is used to tag commits and releases.
Commit messages follow [Convential Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification.

The version number is stored in file `VERSION` to be used programmatically.

From version 1.0.0 the working name is changed into the official name of the package.

## Environment

The code in this repository is developed with Python 3.10.

The package must be installed before using the code in the repository. To install from source (i.e. code in `src` directory), launch the following command in the root directory of the repository (or in general where the file `pyproject.toml` is):

```
pip install .
```

To install the package while allowing changes to its Python code, add flag `--editable` to the previous command (cf. [official guide](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode)).

## Naming convention

In this section some word choices appearing in the documents of this repository are presented, to clarify their meaning.

- The term "dataset" is used with two slightly different meanings. An actual dataset, i.e. a set of climate data, which can be available in multiple formats and files, is referred to as *dataset*. An example is ERA5 dataset by ECMWF. The `xarray.Dataset` class is a Python class provided by package `xarray` and it can be mapped to a dataset. Both the class and its instances are refferred to as either *xarray Dataset* or `xarray.Dataset`.

## Workflow

Notebooks in the main directory show the steps for the analysis. They should be executed in the following order, forming a sort of pipeline:

1. normalise raw data to common format and coordinates with `preprocessing.ipynb`;
2. apply temperature correction to NEX-GDDP-CMIP6 data with `fix_tas_extremes.ipynb`;
3. prepare climatology data by launching `climatology.ipynb`;
4. apply bias adjustment to preprocessed data with `bias_adjustment.ipynb`;
5. evaluate indicators and their variations with `variations.ipynb`, run this notebook for each scenario (must be selected in the specific variable inside the notebook).

Note that steps following step 3 do not depend on it: climatology is needed to evaluate normals and anomalies of climate variables, but analyses on indicators are performed on model data.

## Color palette

File `palette.json` stores colors used in the thesis document and in some plots.

## License

Every file in this repository is covered by the license described in file `LICENSE`.
There are some exceptions, which are described below.

Exposure and vulnerability data on Ciampino's airport contained in files `data/ciampino/exposure.csv`, `data/ciampino/sensitivity.csv` and `data/ciampino/adaptivecapacity.csv` are collected from articles on [extreme temperature events](https://doi.org/10.1016/j.cliser.2023.100390) and [extreme precipitation events](https://doi.org/10.3390/su15097300) by De Vivo et al. which are under [Creative Commons Attribution (CC BY)](https://creativecommons.org/licenses/by/4.0/) license.

To create plots projected on maps the Python package [`cartopy`](https://doi.org/10.5281/zenodo.1182735) is used. Basemaps are from [Natural Earth](https://www.naturalearthdata.com/) and border data are provided by [GADM](https://gadm.org/).
