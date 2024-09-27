if __name__ == "__main__":
    # Imports are here and not outside to speed up script if not run directly (e.g. in case of import elsewhere).
    import xarray
    
    from braun.utils import (aggregation, generic)
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
    
    INDICATORS_INTEGER = (
        "heat_wave_index",
        "heat_wave_max_length",
        "wetdays",
        "cwd"
    )
    
    def _aggregate(experiments, periods, models, indicators, dir_indicators):
        for e in experiments:
            for y in periods:
                for m in models:
                    for i in indicators:
                        filename = dir_indicators / e / y / f"{m}_{i}.nc"
                        if not filename.exists():
                            print(f"Skip non-existing file {filename}")  # TODO better put in proper logging system.
                            continue
                        # Else apply aggregation to indicator.
                        ds = None
                        if i in INDICATORS_INTEGER:
                            ds = generic.open_dataset_NaT(filename)
                        else:
                            ds = xarray.open_dataset(filename)
                        dir_field = filename.parent / "field"
                        dir_field.mkdir(parents=True, exist_ok=True)
                        ds_field = aggregation.aggregate_temporal(ds, path=dir_field / filename.name)
                        # The actual spatial aggregation is made on anomalies,
                        # but keep anyway because it may become useful.
                        dir_hazard = filename.parent / "hazard"
                        dir_hazard.mkdir(parents=True, exist_ok=True)
                        aggregation.aggregate_spatial(ds_field, path=dir_hazard / filename.name)
                        ds.close()  # Release resources, put here to allow chunks loading above.
    
    def _aggregate_anomaly(scenarios, periods, models, indicators, dir_indicators):
        for m in models:
            for i in indicators:
                # Indicator on reference period must exist.
                filename_ref = dir_indicators / "historical" / "reference" / "field" / f"{m}_{i}.nc"
                if not filename_ref.exists():
                    print(f"File {filename_ref} does not exist for reference period, hence no calculation are made")  # TODO better put in proper logging system.
                    continue
                ds_reference = None
                if i in INDICATORS_INTEGER:
                    ds_reference = generic.open_dataset_NaT(filename_ref)
                else:
                    ds_reference = xarray.open_dataset(filename_ref)
                for s in scenarios:
                    for y in periods:
                        filename = dir_indicators / s / y / "field" / f"{m}_{i}.nc"
                        if not filename.exists():
                            print(f"Skip non-existing file {filename}")  # TODO better put in proper logging system.
                            continue
                        # Else evaluate anomaly and apply aggregation.
                        ds_scenario = None
                        if i in INDICATORS_INTEGER:
                            ds_scenario = generic.open_dataset_NaT(filename)
                        else:
                            ds_scenario = xarray.open_dataset(filename)
                        ds = ds_scenario - ds_reference
                        dir_hazard_anomaly = filename.parent.parent / "hazard_anomaly"
                        dir_hazard_anomaly.mkdir(parents=True, exist_ok=True)
                        aggregation.aggregate_spatial(ds, path=dir_hazard_anomaly / filename.name)
                        ds_reference.close()  # Release resources, put here to allow chunks loading above.
                        ds_scenario.close()  # Release resources, put here to allow chunks loading above.
    
    _aggregate(("historical",), ("reference",), thesis.models, indicators, dir_indicators)
    _aggregate(thesis.scenarios, thesis.time_horizons.keys(), thesis.models, indicators, dir_indicators)
    _aggregate_anomaly(thesis.scenarios, thesis.time_horizons.keys(), thesis.models, indicators, dir_indicators)
