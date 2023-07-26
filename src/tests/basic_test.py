import pandas as pd 
import os
from scenario_assessment.filter import FilterResults

def main():

    path = "./data"

    climate = pd.read_csv(os.path.join(path, "total_emissions.csv"), index_col =0)
    eutrophication = pd.read_csv(os.path.join(path, "eutrophication_total.csv"), index_col =0)
    air = pd.read_csv(os.path.join(path, "air_quality_total.csv"), index_col =0)
    products = pd.read_csv(os.path.join(path, "beef_and_milk.csv"), index_col =0)

    emission_dict = {"climate_change": climate,
        "air_quality": air,
        "eutrophication":eutrophication,
        "protein_output": products}

    target = 0.02
    gas = "CH4"

    filter_class = FilterResults(target, gas, emission_dict)

    print(filter_class.total_gwp_gas)

    search_results = filter_class.search()

    print(search_results)


if __name__ == "__main__":
    main()