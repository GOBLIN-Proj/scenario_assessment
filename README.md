# 💻 Static Scenario Generator, for the generation of non randomised scenarios for GOBLIN

 This module was constructed to assess and rank [GOBLIN](https://gmd.copernicus.org/articles/15/2239/2022/) (**G**eneral **O**verview for a **B**ackcasting approach of **L**ivestock **IN**tensification) scenarios.

The latest iterations of GOBLIN systematically produce a range of environmental impacts, as well as livestock ouput data (total protein). Scenario outputs are ranked according to thier overall environmental change, and the change to the baseline livestock outouts. 

Scenarios the meet a specified environmental objective are sorted and ranked. The cost to livestock output is prioritised, with the environmental parameters then factored at varios weights. 

        climate_weight = .8 
        eutrophication_weight = .7
        ammonia_weight = .6

## Installation

Install from git hub. 

When prompted enter your ```<username>``` and password, which is your ```<access_token>```.

```<access_token>``` is provided by the repo manager.

```<username>``` pass your own github username.


```bash
pip install "scenario_assessment@git+https://github.com/colmduff/scenario_assessment.git@main" 

```

## Usage
The results of the scenarios are passed, using a dictionary, to the FilterResults class. 

In addition, the target amount is also passed, as a proportion. As well as the selected global warming gas.

The search() method is used to rank results.

```python
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
```

## License
This project is licensed under the terms of the MIT license.
