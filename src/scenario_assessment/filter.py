from scenario_assessment.filter_tools import Node, StackFrontier, ProteinCalc
import pandas as pd

class FilterResults:
    """A class used to filter the results based on a particular gas reduction target. The class ranks the outputs that meet the selected
    reduction target. Costing is calculated based on the impacts to overall livestock (beef and milk) outputs.

    Attributes
    ----------
    target: float
        the percentage reduction to be achieved, input as a value between 0 and 1

    gas: str
        the green house gas that is the subject of analysis (CH4, N2O, CO2, CO2e)

    total_gwp_gas: dataframe
        A dataframe that contains the greenhouse gas emissions for each scenario and the baseline.

    total_ammonia_gas: dataframe
        A dataframe that contains the ammonia emissions for each scenario and the baseline.

    total_eutrophication: dataframe
        A dataframe that contains the eutrophication emissions for each scenario and the baseline.

    livestock_products: dataframe
        A dataframe that contains the total beef and milk output for each scenario and the baseline.


    Methods
    -------
    target():
        set the percentage reduction, requires a value between 0 and 1.

    gas():
        sets the target gas, value passed as str.

    search():
        returns a nested dictionary containing the rank, gas and percentage reductions in emissions relative to the baseline.

    """

    def __init__(self, target, gas, data_dict):
        self.target = float(target)
        self.gas = gas
        self.total_gwp_gas = data_dict["climate_change"]
        self.total_ammonia_gas = data_dict["air_quality"]
        self.total_eutrophication = data_dict["eutrophication"]
        self.livestock_products = data_dict["protein_output"]


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
        """Filters through the results and gathers the scenarios that meet or exceed the target reduction in the
        specified gas. Each scenario is assigned a cost based on the over all reduction in livestock output (combined milk and beef).
        Scenarios that meet the target and minimise reductions in livestock output are ranked higher than those that have greater reductions
        in livestock outputs.

        Milk and beef are converted to total protein, based on data provided by the EU commission. Protein values for Milk (3.5% fat, boiled)
        and beef (average) are given as 3.1 and 16.9 g/100 gram, respectively.

        Further, the over percetange reduction eutrophication and ammonia emissions are also returned as part of the dictionary.

        These outputs can all be plotted using the rank_chart method in the DataGrapher.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Examples
        --------
        >>> target = 0.02
            gas = "CO2e"

            filter = Filter_results(target, gas)

            result = filter.search()
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
            
            total_cost = frontier.combined_score_calculation(node.gas_change, node.eutrophication_cost, node.ammonia_cost, node.production_cost)
            
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