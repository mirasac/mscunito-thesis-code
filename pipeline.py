if __name__ == "__main__":
    # Imports are here and not outside to speed up script if not run directly (e.g. in case of import elsewhere).
    import pandas
    import xarray
    
    from braun.utils import (aggregation, csvparser, generic)
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
            # Keep EOF basis, note that coordinates are the same among all experiments,
            # hence it is possible to project onto historical experiment basis.
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
                    # Transform the field, this is the actual spatial aggregation.
                    dir_hazard_rotated = filename.parent / "hazard_rotated"
                    dir_hazard_rotated.mkdir(parents=True, exist_ok=True)
                    _da = model.transform(ds_field, normalized=False).sel(mode=1, drop=True)
                    _da.attrs.pop("solver_kwargs", None)  # This variable gives problems when saving NetCDF. 
                    _ds = _da.to_dataset(name=i)
                    _ds.to_netcdf(dir_hazard_rotated / filename.name)
                    # Transform the anomaly.
                    dir_hazard_anomaly = filename.parent / "hazard_anomaly"
                    dir_hazard_anomaly.mkdir(parents=True, exist_ok=True)
                    ds_anomaly = ds_field - ds_field_ref
                    _da = model.transform(ds_anomaly, normalized=False).sel(mode=1, drop=True)
                    _da.attrs.pop("solver_kwargs", None)  # This variable gives problems when saving NetCDF. 
                    _ds = _da.to_dataset(name=i)
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
            ds_z_score = (ds_historical - mu) / sigma
            dir_normalized = dir_indicators / "historical" / "reference" / "normalized"
            dir_normalized.mkdir(parents=True, exist_ok=True)
            ds_z_score.to_netcdf(dir_normalized / filename)
            for s in thesis.scenarios:
                for y in thesis.time_horizons.keys():
                    ds_scenario = xarray.load_dataset(dir_indicators / s / y / "hazard_rotated" / filename, decode_timedelta=False)
                    ds_z_score = (ds_scenario - mu) / sigma
                    dir_normalized = dir_indicators / s / y / "normalized"
                    dir_normalized.mkdir(parents=True, exist_ok=True)
                    ds_z_score.to_netcdf(dir_normalized / filename)
    
    
    
    ######### Evaluate system-dependent indicators #########
    
    df_E = csvparser.load_indicators(dir_indicators / "exposure.csv")
    
    df_a = csvparser.load_indicators(dir_indicators / "adaptivecapacity.csv")
    df_s = csvparser.load_indicators(dir_indicators / "sensitivity.csv")
    df_V = pandas.concat([df_a, df_s])
    
    
    
    ######### Evaluate scalar values #########
    
    # Evaluate scalar value for exposure.
    exposure = df_E["value"].mean(axis=0, skipna=True)  # Weighted mean with unitary weights.
    
    # Evaluate scalar value for vulnerability.
    vulnerability = df_V["value"].mean(axis=0, skipna=True)  # Weighted mean with unitary weights.
    
    # Evaluate scalar values for hazard and risk.
    def evaluate_hazard(model, experiment, period, dir_data):
        dir_normalized = dir_data / experiment / period / "normalized"
        list_da = []
        for i in thesis.INDICATORS:
            ds = xarray.load_dataset(dir_normalized / f"{model}_{i}.nc", decode_timedelta=False)
            ds = generic.rename_coords(ds, i, '_')
            list_da.append(ds[i])
        da = sum(list_da) / len(list_da)  # Weighted mean with unitary weights.
        ds = da.to_dataset(name="hazard")
        dir_scalar = dir_normalized.parent / "scalar"
        dir_scalar.mkdir(parents=True, exist_ok=True)
        ds.to_netcdf(dir_scalar / f"{model}.nc")
        return ds
    
    def evaluate_risk(model, experiment, period, exposure, hazard, vulnerability, dir_data):
        risk = (exposure + hazard + vulnerability) / 3.0  # Weighted mean with unitary weights.
        risk = risk.rename({"hazard": "risk"})
        dir_out = dir_data / experiment / period / "risk"
        dir_out.mkdir(parents=True, exist_ok=True)
        risk.to_netcdf(dir_out / f"{model}.nc")
        return risk
    
    for m in thesis.models:
        hazard = evaluate_hazard(m, "historical", "reference", dir_indicators)
        evaluate_risk(m, "historical", "reference", exposure, hazard, vulnerability, dir_indicators)
        for s in thesis.scenarios:
            for y in thesis.time_horizons.keys():
                hazard = evaluate_hazard(m, s, y, dir_indicators)
                evaluate_risk(m, s, y, exposure, hazard, vulnerability, dir_indicators)
    
    
    
    ######### Evaluate risk categories #########
    
    def get_risk_ensemble(experiment, period, dir_indicators):
        problem = "heat_wave_max_length_thresh_tasmin"
        list_ds = []
        for m in thesis.models:
            ds = xarray.load_dataset(dir_indicators / experiment / period / "risk" / f"{m}.nc", decode_timedelta=False)
            end = ds.sizes[problem]  # Cheat: it is known that the NaNs are at the end of the array.
            ds = ds.drop_vars(ds.coords.keys())
            ds = ds.assign_coords(coords={problem: (problem, thesis.p3[:end])})
            list_ds.append(ds)
        dim_m = "model"
        ds = xarray.concat(list_ds, dim=dim_m)
        ds = ds.assign_coords({dim_m: (dim_m, list(thesis.models))})
        return ds

    def aggregate_risk_average(ds):
        da = ds["risk"]
        # TODO note that not only the quantiles are very slow to compute,
        # but it seems that the other dimensions are not kept.
        #quantiles = da.quantile([0.05, 0.2, 0.4, 0.5, 0.6, 0.8, 0.95], dim="model", method="linear", skipna=True),
        return xarray.Dataset(data_vars={
            "mean": da.mean(dim="model", skipna=True),
            "std": da.std(dim="model", skipna=True, ddof=1),
            "min": da.min(dim="model", skipna=True),
            #"P05": quantiles.isel(quantile=0, drop=True),
            #"P20": quantiles.isel(quantile=1, drop=True),
            #"P40": quantiles.isel(quantile=2, drop=True),
            #"P50": quantiles.isel(quantile=3, drop=True),
            #"P60": quantiles.isel(quantile=4, drop=True),
            #"P80": quantiles.isel(quantile=5, drop=True),
            #"P95": quantiles.isel(quantile=6, drop=True),
            "max": da.max(dim="model", skipna=True)
        })
    
    def apply_risk_categories(da, thresholds):
        """Apply risk categories as natural numbers from 1 to
        len(thresholds) - 1 using the boundaries specified
        in array `thresholds`. Values lower than the first value
        and higher than the last value are assigned to the
        lowest and highest risk categories, respectively.
        """
        cond = (da <= thresholds[0])
        da = xarray.where(cond, 1, da, keep_attrs=True)
        for i, _ in enumerate(thresholds[1:], start=1):
            cond = ((da > thresholds[i - 1]) & (da <= thresholds[i]))
            da = xarray.where(cond, i, da, keep_attrs=True)
        cond = (da > thresholds[-1])
        da = xarray.where(cond, len(thresholds) - 1, da, keep_attrs=True)
        return da
    
    coords = {f"{i}_{p}": (f"{i}_{p}", values) for i, parameters in thesis.PARAMETERS.items() for p, values in parameters.items()}
    
    ds = aggregate_risk_average(get_risk_ensemble("historical", "reference", dir_indicators))
    ds = ds.assign_coords(coords=coords)
    thresholds = braun.utils.generic.get_risk_thresholds(ds["mean"].values.flatten(), n_categories=len(thesis.risk_categories))
    ds = ds.assign({"category": apply_risk_categories(ds["mean"], thresholds)})
    ds.to_netcdf(dir_indicators / "historical" / "reference" / "risk" / "ensemble.nc")
    for s in thesis.scenarios:
        for y in thesis.time_horizons.keys():
            ds = aggregate_risk_average(get_risk_ensemble(s, y, dir_indicators))
            ds = ds.assign_coords(coords=coords)
            ds = ds.assign({"category": apply_risk_categories(ds["mean"], thresholds)})
            ds.to_netcdf(dir_indicators / s / y / "risk" / "ensemble.nc")
