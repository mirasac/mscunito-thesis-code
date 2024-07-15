# mscunito-thesis-code

Sources for thesis code.

## Versioning

[SemVer 2.0.0](https://semver.org/spec/v2.0.0.html) is used to tag commits and releases.
Commit messages follow [Convential Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification.

## Environment

The code in this repository is developed with Python 3.10.

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

## Color palette

File `palette.json` stores colors used in the thesis document and in some plots.
