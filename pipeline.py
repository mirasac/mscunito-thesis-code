if __name__ == "__main__":
    # Imports are here and not outside to speed up script if not run directly (e.g. in case of import elsewhere).
    import xarray
    
    from braun.utils import (aggregation, generic)
    import braun.packages.xeofs
    import settings
    import thesis
    
    dir_data = settings.dir_data / settings.site
    
    
    
    ######### Aggregate hazard indicators #########
    
    # TODO these variables would be defined earlier in the pipeline,
    # use them when the pipeline is complete.
    dir_indicators = dir_data / "indicators"
    indicators = thesis.INDICATORS
    indicators_integer = thesis.INDICATORS_INTEGER
    indicators_invalid = thesis.INDICATORS_INVALID
    
    for m in thesis.models:
        for i in indicators:
            # First aggregate indicators of reference period.
            filename = dir_indicators / "historical" / "reference" / f"{m}_{i}.nc"
            if not filename.exists():
                print(f"Skip non-existing file {filename}")  # TODO better put in proper logging system.
                continue
            # Else apply aggregation to indicator.
            ds = None
            if i in indicators_integer:
                ds = generic.open_dataset_NaT(filename)
            else:
                ds = xarray.open_dataset(filename)
            _ds = ds
            # Remove invalid combinations of parameters, otherwise EOF breaks.
            if i in indicators_invalid:
                _ds = _ds.dropna(dim="thresh_tasmin", how="any")
            # Aggregate temporal dimension.
            dir_field = filename.parent / "field"
            dir_field.mkdir(parents=True, exist_ok=True)
            _dir = dir_field.resolve() / "std"
            _dir.mkdir(parents=True, exist_ok=True)
            _ds.std(dim="time", skipna=False, ddof=1).to_netcdf(path=_dir / filename.name)
            _ds, = aggregation.aggregate_temporal(_ds, path=dir_field / filename.name, skipna=False)
            # Aggregate spatial dimension.
            dir_hazard = filename.parent / "hazard"
            dir_hazard.mkdir(parents=True, exist_ok=True)
            ds_field_ref = _ds.chunk(chunks={"latitude": -1, "longitude": -1})
            _, model = aggregation.aggregate_spatial(ds_field_ref, path=dir_hazard / filename.name)
            braun.packages.xeofs.save(model, dir_hazard / f"{filename.name}.xeofs")
            ds.close()  # Release resources, put here to allow chunks loading above.
            
            # Then aggregate indicators of future periods.
            for s in thesis.scenarios:
                for y in thesis.time_horizons.keys():
                    filename = dir_indicators / s / y / f"{m}_{i}.nc"
                    if not filename.exists():
                        print(f"Skip non-existing file {filename}")  # TODO better put in proper logging system.
                        continue
                    # Else apply aggregation to indicator.
                    ds = None
                    if i in indicators_integer:
                        ds = generic.open_dataset_NaT(filename)
                    else:
                        ds = xarray.open_dataset(filename)
                    _ds = ds
                    # Remove invalid combinations of parameters, otherwise EOF breaks.
                    if i in indicators_invalid:
                        _ds = _ds.dropna(dim="thresh_tasmin", how="any")
                    # Aggregate temporal dimension.
                    dir_field = filename.parent / "field"
                    dir_field.mkdir(parents=True, exist_ok=True)
                    _dir = dir_field.resolve() / "std"
                    _dir.mkdir(parents=True, exist_ok=True)
                    _ds.std(dim="time", skipna=False, ddof=1).to_netcdf(path=_dir / filename.name)
                    _ds, = aggregation.aggregate_temporal(_ds, path=dir_field / filename.name, skipna=False)
                    # Aggregate spatial dimension.
                    dir_hazard = filename.parent / "hazard"
                    dir_hazard.mkdir(parents=True, exist_ok=True)
                    ds_field = _ds.chunk(chunks={"latitude": -1, "longitude": -1})
                    _, _model = aggregation.aggregate_spatial(ds_field, path=dir_hazard / filename.name)
                    braun.packages.xeofs.save(_model, dir_hazard / f"{filename.name}.xeofs")
                    # The actual spatial aggregation is made on anomalies.
                    dir_hazard_anomaly = filename.parent / "hazard_anomaly"
                    dir_hazard_anomaly.mkdir(parents=True, exist_ok=True)
                    ds_anomaly = ds_field - ds_field_ref
                    # Note that coordinates are the same among all experiments,
                    # hence it is possible to project onto historical experiment basis.
                    _da = model.transform(ds_anomaly, normalized=False).sel(mode=1, drop=True)
                    _da.attrs.pop("solver_kwargs", None)  # This variable gives problems when saving NetCDF. 
                    _ds = _da.to_dataset(name=list(ds.data_vars.keys())[0])  # Datasets have only one variable.
                    _ds.to_netcdf(dir_hazard_anomaly / filename.name)
                    ds.close()  # Release resources, put here to allow chunks loading above.
    
    
    
    ######### Normalise hazard indicators #########
    
    for m in thesis.models:
        for i in indicators:
            filename = f"{m}_{i}.nc"
            # Use decode_timedelta=False because although values are already float,
            # sometimes they are loaded as timedelta,
            # probably because they are truncated at the right number of decimal places
            # and they are all positive.
            ds_historical = xarray.load_dataset(dir_indicators / "historical" / "reference" / "hazard" / filename, decode_timedelta=False)
            mu = ds_historical.mean(skipna=True)
            sigma = ds_historical.std(skipna=True, ddof=1)
            for s in thesis.scenarios:
                for y in thesis.time_horizons.keys():
                    ds_scenario = xarray.load_dataset(dir_indicators / s / y / "hazard_anomaly" / filename, decode_timedelta=False)
                    ds_z_score = (ds_scenario - mu) / sigma
                    dir_normalized = dir_indicators / s / y / "normalized"
                    dir_normalized.mkdir(parents=True, exist_ok=True)
                    ds_z_score.to_netcdf(dir_normalized / filename)
