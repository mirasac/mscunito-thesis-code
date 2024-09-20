if __name__ == "__main__":
    # Imports are here and not outside to speed up script if not run directly (e.g. in case of import elsewhere).
    import xarray
    
    from braun.utils import aggregation
    import settings
    import thesis
    
    dir_data = settings.dir_data / settings.location
    
    
    
    ######### Aggregate hazard indicators #########
    
    # TODO: these variables are defined earlier in the pipeline,
    # use them when the pipeline is complete.
    dir_indicators = dir_data / "indicators"
    indicators = (
        "heat_wave_index",
        "heat_wave_max_length",
        "max_n_day_precipitation_amount",
        "wetdays",
        "cwd"
    )
    
    experiments = ["historical"]
    experiments.extend(thesis.scenario)
    periods = ["reference"]
    periods.extend(thesis.time_horizons.keys())
    for e in experiments:
        for m in thesis.models:
            for i in indicators:
                for y in periods:
                    filename = dir_indicators / e / f"{m}_{i}_{y}.nc"
                    if not filename.exists():
                        continue
                    # Else apply aggregation to indicator.
                    ds = xarray.open_dataset(filename, decode_timedelta=False)
                    dir_field = filename.parent / "field"
                    dir_field.mkdir(parents=True, exist_ok=True)
                    ds_field = aggregation.aggregate_temporal(ds, path=dir_field / filename.name)
                    dir_hazard = filename.parent / "hazard"
                    dir_hazard.mkdir(parents=True, exist_ok=True)
                    ds_hazard = aggregation.aggregate_spatial(ds_field, path=dir_hazard / filename.name)
