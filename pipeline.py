if __name__ == "__main__":
    # Imports are here and not outside to speed up script if not run directly (e.g. in case of import elsewhere).
    import xarray
    
    from braun.utils import aggregation
    import settings
    import thesis
    
    dir_data = settings.dir_data / settings.site
    
    
    
    ######### Aggregate hazard indicators #########
    
    # TODO these variables would be defined earlier in the pipeline,
    # use them when the pipeline is complete.
    dir_indicators = dir_data / "indicators"
    indicators = (
        "heat_wave_index",
        "heat_wave_max_length",
        "max_n_day_precipitation_amount",
        "wetdays",
        "cwd"
    )
    
    def aggregate(experiments, periods, models, indicators, dir_indicators):
        for e in experiments:
            for y in periods:
                for m in models:
                    for i in indicators:
                        filename = dir_indicators / e / y / f"{m}_{i}.nc"
                        if not filename.exists():
                            print(f"Skip non-existing file {filename}")  # TODO better put in proper logging system.
                            continue
                        # Else apply aggregation to indicator.
                        # Beware that xarray reads integer numbers in
                        # NetCDF files as time intervals by default. This
                        # means that the numerical representation of
                        # NaT values is loaded, instead of setting NaN. This
                        # further operation is done manually by exploiting the
                        # fact that only some indicators result in
                        # integer values which are always non negative.
                        if i in ("heat_wave_index", "heat_wave_max_length", "wetdays", "cwd"):
                            decode_timedelta = False
                        else:
                            decode_timedelta = True
                        ds = xarray.open_dataset(filename, decode_timedelta=decode_timedelta)
                        if not decode_timedelta:
                            ds = ds.where((ds >= 0))
                        dir_field = filename.parent / "field"
                        dir_field.mkdir(parents=True, exist_ok=True)
                        ds_field = aggregation.aggregate_temporal(ds, path=dir_field / filename.name)
                        dir_hazard = filename.parent / "hazard"
                        dir_hazard.mkdir(parents=True, exist_ok=True)
                        aggregation.aggregate_spatial(ds_field, path=dir_hazard / filename.name)
    
    aggregate(("historical",), ("reference",), thesis.models, indicators, dir_indicators)
    aggregate(thesis.scenarios, thesis.time_horizons.keys(), thesis.models, indicators, dir_indicators)
