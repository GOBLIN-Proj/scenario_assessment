"""
Filter Results Module
---------------------
This module contains the FilterResults class, which is used to filter the results based on a particular gas reduction target.

"""

from scenario_assessment.filter_tools import Node, StackFrontier, ProteinCalc
import pandas as pd

class FilterResults:
    """
    A class used to filter results based on a specified target for greenhouse gas reduction. It ranks scenarios based on their ability
    to meet the reduction target while minimizing impacts on livestock outputs (beef and milk).

    Attributes
    ----------
    target : float
        The target percentage reduction to be achieved, input as a value between 0 and 1.
    gas : str
        The greenhouse gas that is the subject of analysis (e.g., CH4, N2O, CO2, CO2e).
    total_gwp_gas : DataFrame
        A dataframe containing the greenhouse gas emissions for each scenario compared to the baseline.
    total_ammonia_gas : DataFrame
        A dataframe containing the ammonia emissions for each scenario compared to the baseline.
    total_eutrophication : DataFrame
        A dataframe containing the eutrophication emissions for each scenario compared to the baseline.
    livestock_products : DataFrame
        A dataframe containing the total beef and milk output for each scenario compared to the baseline.
    climate_weight : float, optional
        The weighting applied to the climate change impact in the overall score. Default is 0.5.
    ammonia_weight : float, optional
        The weighting applied to the ammonia emissions impact in the overall score. Default is 0.2.
    eutrophication_weight : float, optional
        The weighting applied to the eutrophication impact in the overall score. Default is 0.3.

    Methods
    -------
    target(value):
        Sets the percentage reduction target. Requires a value between 0 and 1.

    gas(value):
        Sets the target greenhouse gas. The value is passed as a string.

    search():
        Filters scenarios based on the specified reduction target and ranks them according to their impact on livestock outputs 
        and environmental factors. Returns a nested dictionary containing the rankings, target gas, and percentage reductions in 
        emissions relative to the baseline.

    Raises
    ------
    ValueError:
        If the sum of the environmental impact weights (climate, ammonia, eutrophication) exceeds 1.

    Example
    -------
    >>> data_dict = {
            "climate_change": df_climate,
            "air_quality": df_ammonia,
            "eutrophication": df_eutrophication,
            "protein_output": df_livestock
        }
    >>> filter_results = FilterResults(0.25, 'CO2e', data_dict)
    >>> filter_results.search()
    """

    def __init__(self, target, gas, data_dict, climate_weight=0.5, ammonia_weight=0.2, eutrophication_weight=0.3):
        self.target = float(target)
        self.gas = gas
        self.total_gwp_gas = data_dict["climate_change"]
        self.total_ammonia_gas = data_dict["air_quality"]
        self.total_eutrophication = data_dict["eutrophication"]
        self.livestock_products = data_dict["protein_output"]
        self.climate_weight = climate_weight
        self.ammonia_weight = ammonia_weight
        self.eutrophication_weight = eutrophication_weight

        # Validate that the sum of the weights does not exceed 1
        total_weight = self.climate_weight + self.eutrophication_weight + self.ammonia_weight

        if total_weight > 1:
            raise ValueError(f"The sum of the weights ({total_weight}) exceeds 1. Adjust the weights so their sum does not exceed 1.")


    @property  # getter
    def target(self):
        return self._target


    @target.setter
    def target(self, target):
        """Sets the percentage reduction for the selected gas. Input must be a float between 0 and 1.

        Parameters
        ----------
        target: float
            value between 0 and 1

        Returns
        -------
        None

        Examples
        --------
        >>> target = 0.02
            gas = "CO2e"

            filter = Filter_results(target, gas)

            target = 0.5

            filter.target(target)
        """
        if target <= 0 or target > 1:
            raise ValueError(
                "Invalid amount, target must be a value greater than 0 and less than 1"
            )

        self._target = target

    @property  # getter
    def gas(self):
        return self._gas

    @gas.setter
    def gas(self, gas):
        """Sets the target gas. Input must be a str in ["CH4", "N2O","CO2", "CO2E"].

        Input is case insensitive.

        Parameters
        ----------
        gas: str
            input one of ["CH4", "N2O","CO2", "CO2E"]

        Returns
        -------
        None

        Examples
        --------
        >>> target = 0.02
            gas = "CO2e"

            filter = Filter_results(target, gas)

            gas = "ch4"

            filter.gas(gas)
        """
        valid_gases = ["CH4", "N2O", "CO2", "CO2E"]
        if gas.upper() not in valid_gases:
            raise ValueError("Gas not Valid")

        if gas.upper() != "CO2E":
            self._gas = gas.upper()
        else:
            self._gas = "CO2e"


    def search(self):
        """
        Searches through greenhouse gas reduction scenarios to identify those that meet or exceed a target reduction 
        in a specified greenhouse gas, considering the environmental and economic impacts on livestock production.
        Each scenario is evaluated based on the overall reduction in livestock output, including both milk and beef, 
        converted to total protein as per EU commission standards. Additionally, the method assesses the percentage 
        reduction in ammonia emissions and eutrophication.

        The method ranks scenarios based on their ability to minimize reductions in livestock output while meeting 
        greenhouse gas reduction targets. It utilizes internal class attributes for environmental and production data 
        analysis. Results can be visualized using the 'rank_chart' method in the DataGrapher.

        Returns:
            dict: A dictionary containing ranked scenarios with the following keys:
                'rank': The scenario's rank based on the combined environmental and production cost.
                'gas': The target greenhouse gas.
                'gas_change': The percentage reduction in the target gas compared to the base scenario.
                'ammonia_change': Percentage reduction in ammonia emissions compared to the base scenario.
                'eutrophication_change': Reduction in eutrophication emissions compared to the base scenario.
                'production_cost': The cost impact on livestock outputs.
                'total_cost': Combined environmental and production cost.

        Raises:
            ValueError: If no scenarios meet the reduction criteria.

        Examples:
            >>> target_reduction = 0.02
            >>> target_gas = "CO2e"
            >>> filter_results = FilterResults(target_reduction, target_gas)
            >>> result = filter_results.search()
            >>> print(result)

        Note:
            This method assumes the presence of class attributes such as 'total_gwp_gas' and 'livestock_products' 
            containing the necessary environmental and livestock production data, respectively. It also relies on 
            methods like 'env_cost_calculation' and 'production_cost_calculation' for calculating the environmental 
            and production costs associated with each scenario.
        """
        calculator = ProteinCalc()

        starting_state = self.total_gwp_gas.loc[-1, self.gas]


        scenarios_df = pd.DataFrame(columns=["scenario", self.gas])


        scenarios_df["scenario"] = self.total_gwp_gas[self.total_gwp_gas.index != -1].index.tolist()
        scenarios_df[self.gas] = self.total_gwp_gas.loc[(self.total_gwp_gas.index != -1),self.gas]
        scenarios_df.set_index("scenario", inplace=True)

        initial_node = Node(
            state=starting_state,
            scenario=None,
            gas_change = None,
            production_cost=None,
            ammonia_cost=None,
            eutrophication_cost=None,
        )

        # use quefrontier, depth first search takes a really long time
        frontier = (
            StackFrontier()
        )  # FIFO, breath first search, stack is depth first search

        # build Frontier
        base_livestock_inputs = calculator.milk_protein_calculator(self.livestock_products.loc[-1, "total_milk_kg"]) + calculator.beef_protein_calculator(self.livestock_products.loc[-1, "total_beef_kg"])
        base_ammonia_inputs = self.total_ammonia_gas.loc[-1, "Total"]
        base_eutrophication_inputs = self.total_eutrophication.loc[-1, "Total"]

        for sc in scenarios_df.index:
            sc_livestock_inputs = calculator.milk_protein_calculator(self.livestock_products.loc[sc, "total_milk_kg"]) + calculator.beef_protein_calculator(self.livestock_products.loc[sc, "total_beef_kg"])
            
            sc_ammonia_inputs = self.total_ammonia_gas.loc[sc, "Total"]
            sc_eutrophication_inputs = self.total_eutrophication.loc[sc, "Total"]
            sc_gas_inputs = self.total_gwp_gas.loc[sc, self.gas]


            frontier.add(
                Node(
                    state=scenarios_df.loc[sc, self.gas],
                    scenario=sc,
                    gas_change=frontier.env_cost_calculation(scenarios_df.loc[sc, self.gas], initial_node.state),
                    production_cost=frontier.production_cost_calculation(
                        sc_livestock_inputs, base_livestock_inputs
                    ),
                    ammonia_cost=frontier.env_cost_calculation(
                        sc_ammonia_inputs, base_ammonia_inputs
                    ),
                    eutrophication_cost=frontier.env_cost_calculation(
                        sc_eutrophication_inputs, base_eutrophication_inputs
                    ),
                )
            )

           

        # the explored set
        explored_nodes_matched = set()
        explored_nodes = set()

        # emission results
        emission_result = []

        # GHG target
        ghg_target = initial_node.state - (initial_node.state * self.target)
 
        # Keep looping until solution found

        for index in range(len(frontier.frontier)):
            node = frontier.frontier[index]

            if node not in explored_nodes:

                if node.state <= ghg_target:

                    emission_result.append((node.scenario, node.state))
                    explored_nodes_matched.add(node)

                explored_nodes.add(node)

        # empty frontier
        count = 0
        for index in range(len(frontier.frontier)):
            node = frontier.frontier[index - count]
            frontier.delete(node)
            count += 1

        costs = []
        for node in explored_nodes_matched:
            
            total_cost = frontier.combined_score_calculation(node.gas_change, node.eutrophication_cost, 
                                                             node.ammonia_cost, node.production_cost, 
                                                             self.climate_weight, self.eutrophication_weight, self.ammonia_weight)
            
            costs.append(
                (
                    node.scenario,
                    node.gas_change,
                    node.production_cost,
                    node.ammonia_cost,
                    node.eutrophication_cost,
                    total_cost
                )
            )

        costs.sort(key=lambda c: c[5], reverse=False)

        keys = dict()

        for index in range(len(costs)):
            keys[costs[index][0]] = {}
            keys[costs[index][0]]["rank"] = index + 1
            keys[costs[index][0]]["gas"] = self.gas
            keys[costs[index][0]]["gas_change"] = costs[index][1]
            keys[costs[index][0]]["ammonia_change"] = costs[index][3]
            keys[costs[index][0]]["eutrophication_change"] = costs[index][4]
            keys[costs[index][0]]["production_cost"] = costs[index][2]
            keys[costs[index][0]]["total_cost"] = costs[index][5]

            # Check if the dictionary is empty
        if not keys:
            # Raise an exception to indicate an error condition
            raise ValueError("No reductions in scenarios were identified.")

        return keys