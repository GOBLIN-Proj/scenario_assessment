import pandas as pd 
import os
from scenario_assessment.filter import FilterResults

def main():

    path = "./data"

    climate = pd.read_csv(os.path.join(path, "climate_change_totals.csv"), index_col =0)
    eutrophication = pd.read_csv(os.path.join(path, "eutrophication_totals_test.csv"), index_col =0)
    air = pd.read_csv(os.path.join(path, "air_quality_totals_test.csv"), index_col =0)
    products = pd.read_csv(os.path.join(path, "protein_and_milk_summary.csv"), index_col =0)

    

    emission_dict = {"climate_change": climate,
        "air_quality": air,
        "eutrophication":eutrophication,
        "protein_output": products}


    target = 0.02
    gas = "CH4"

    climate = 0.3
    eutrophication = 0.3
    ammonia = 0.4

    filter_class = FilterResults(target, gas, emission_dict, climate, eutrophication, ammonia)

    print(filter_class.climate_weight)

    print(filter_class.total_gwp_gas)

    search_results = filter_class.search()

    print(search_results)


if __name__ == "__main__":
    main()