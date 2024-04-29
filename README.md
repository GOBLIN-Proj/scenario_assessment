# 💻 Scenario Assessment Tool for GOBLIN scenarios
[![license](https://img.shields.io/badge/License-MIT-red)](https://github.com/GOBLIN-Proj/scenario_assessment/blob/0.1.0/LICENSE)
[![python](https://img.shields.io/badge/python-3.9-blue?logo=python&logoColor=white)](https://github.com/GOBLIN-Proj/scenario_assessment)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

 This module was constructed to assess and rank [GOBLIN](https://gmd.copernicus.org/articles/15/2239/2022/) (**G**eneral **O**verview for a **B**ackcasting approach of **L**ivestock **IN**tensification) scenarios.

The latest iterations of GOBLIN systematically produce a range of environmental impacts, as well as livestock ouput data (total protein). Scenario outputs are ranked according to thier overall environmental change, and the change to the baseline livestock outouts. 

Scenarios the meet a specified environmental objective are sorted and ranked. The cost to livestock output is prioritised, with the environmental parameters then factored at varios weights. 

        climate_weight = .4
        eutrophication_weight = .3
        ammonia_weight = .3

These weights can be adjusted by the user.

## Installation

Install from git hub. 

```bash
pip install "scenario_assessment@git+https://github.com/GOBLIN-Proj/scenario_assessment.git@main" 

```

Install from PyPI

```bash
pip install scenario_assessment
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
