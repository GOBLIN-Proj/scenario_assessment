"""
Filter tools Module
-------------------

This module contains the classes and functions that are used to filter the scenarios based on the user inputs.

"""

class Node:
    """
    A node representing a specific scenario in environmental impact and cost analysis.

    Parameters
    ----------
    state : float
        The current state or value (e.g., current greenhouse gas emissions).
    scenario : str
        The name or identifier of the scenario being considered.
    gas_change : float
        The percentage change in greenhouse gas emissions for the scenario.
    production_cost : float
        The change in production cost (as a percentage) associated with the scenario.
    ammonia_cost : float
        The change in cost (as a percentage) associated with ammonia emissions for the scenario.
    eutrophication_cost : float
        The change in cost (as a percentage) associated with eutrophication for the scenario.
    """
    def __init__(
        self, state, scenario, gas_change, production_cost, ammonia_cost, eutrophication_cost
    ):
        self.state = state
        self.scenario = scenario
        self.gas_change = gas_change
        self.production_cost = production_cost
        self.ammonia_cost = ammonia_cost
        self.eutrophication_cost = eutrophication_cost


class StackFrontier:
    """
    A class to manage the frontier in a depth-first search algorithm.

    Attributes
    ----------
    frontier : list
        A list of Node objects that are yet to be explored.
    """
    def __init__(self):
        self.frontier = []

    def add(self, node):
        """
        Add a new node to the frontier.

        Parameters
        ----------
        node : Node
            The node to be added to the frontier.
        """
        self.frontier.append(node)

    def contains_state(self, state):
        """
        Check if any node in the frontier has a particular state.

        Parameters
        ----------
        state : float
            The state to be checked.

        Returns
        -------
        bool
            True if a node with the state exists in the frontier; False otherwise.
        """
        return any(node.state == state for node in self.frontier)

    def empty(self):
        """
        Check if the frontier is empty.

        Returns
        -------
        bool
            True if the frontier is empty; False otherwise.
        """
        return len(self.frontier) == 0

    def delete(self, node):
        """
        Remove a node from the frontier.

        Parameters
        ----------
        node : Node
            The node to be removed.

        Raises
        ------
        Exception
            If the frontier is already empty.
        """
        if self.empty():
            raise Exception("empty frontier")
        else:

            self.frontier.remove(node)

    def length(self):
        """
        Get the current length of the frontier.

        Returns
        -------
        int
            The number of nodes currently in the frontier.
        """
        return len(self.frontier)


    @staticmethod
    def production_cost_calculation(sc_inputs, base_inputs):
        """
        Calculate the change in production costs.

        Parameters
        ----------
        sc_inputs : float
            The scenario's input value (e.g., protein production).
        base_inputs : float
            The base case input value for comparison.

        Returns
        -------
        float
            The percentage change in production costs.
        """
        return ((sc_inputs - base_inputs) / base_inputs) * 100


    @staticmethod
    def env_cost_calculation(sc_inputs, base_inputs):
        """
        Calculate the environmental cost change.

        Parameters
        ----------
        sc_inputs : float
            The scenario's environmental metric (e.g., ammonia or eutrophication levels).
        base_inputs : float
            The base case environmental metric for comparison.

        Returns
        -------
        float
            The percentage change in environmental costs.
        """
        cost = ((sc_inputs - base_inputs) / base_inputs) * 100

        return cost
    
    @staticmethod
    def combined_score_calculation(climate, eutrophication, ammonia, production_cost, climate_weight=None, eutrophication_weight=None, ammonia_weight=None):
        """
        Calculate a combined environmental and production score for a scenario.

        This function calculates a weighted score based on changes in climate impact, eutrophication, 
        ammonia emissions, and production costs. Users can provide custom weights for climate, eutrophication, 
        and ammonia impacts. If provided, the sum of these weights must not exceed one to ensure a balanced 
        approach to environmental factors. The total score combines these environmental scores with the 
        absolute value of the production cost change.

        Parameters
        ----------
        climate : float
            The change in climate impact (e.g., greenhouse gas emissions).
        eutrophication : float
            The change in eutrophication impact.
        ammonia : float
            The change in ammonia emissions.
        production_cost : float
            The change in production costs.
        climate_weight : float, optional
            The weight for the climate change impact. Defaults to 0.4.
        eutrophication_weight : float, optional
            The weight for the eutrophication impact. Defaults to 0.3.
        ammonia_weight : float, optional
            The weight for the ammonia emissions impact. Defaults to 0.3.

        Returns
        -------
        float
            The total combined score, taking into account both environmental impacts and production costs. 

        """
        # Set default weights if none provided
        climate_weight = climate_weight or 0.4
        eutrophication_weight = eutrophication_weight or 0.3
        ammonia_weight = ammonia_weight or 0.3

        env_score = (climate * climate_weight) + (eutrophication * eutrophication_weight) + (ammonia * ammonia_weight)
        production_score = abs(production_cost)  # Consider normalizing this if necessary

        total_score = production_score + env_score  # Combine scores from environmental and production impacts

        return total_score

class ProteinCalc:
    """
    A class used to calculate the protein content from milk and beef based on predefined or user-defined protein values.

    Attributes
    ----------
    milk_protein : float
        The amount of protein (in grams) per 100 grams of milk. Default value is set based on typical protein content.
    beef_protein : float
        The amount of protein (in grams) per 100 grams of beef. Default value is set based on typical protein content.

    Methods
    -------
    milk_protein_calculator(milk):
        Calculates the total protein content in a given quantity of milk.
        
    beef_protein_calculator(beef):
        Calculates the total protein content in a given quantity of beef.

    Parameters
    ----------
    milk_protein : float, optional
        The protein content percentage for milk. If not provided, defaults to a typical value.
    beef_protein : float, optional
        The protein content percentage for beef. If not provided, defaults to a typical value.
    """
    def __init__(self, milk_protein=None, beef_protein=None):
        self.milk_protein = milk_protein or 31
        self.beef_protein = beef_protein or 169


    def milk_protein_calculator(self, milk):
        """
        Calculate the total protein content based on the quantity of milk.

        Parameters
        ----------
        milk : float
            The quantity of milk (in grams) for which the protein content is to be calculated.

        Returns
        -------
        float
            The total protein content (in grams) in the specified quantity of milk.
        """
        return self.milk_protein * milk
    

    def beef_protein_calculator(self, beef):
        """
        Calculate the total protein content based on the quantity of beef.

        Parameters
        ----------
        beef : float
            The quantity of beef (in grams) for which the protein content is to be calculated.

        Returns
        -------
        float
            The total protein content (in grams) in the specified quantity of beef.
        """
        return self.beef_protein * beef