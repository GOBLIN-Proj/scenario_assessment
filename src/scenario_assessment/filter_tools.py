class Node:
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
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def delete(self, node):
        if self.empty():
            raise Exception("empty frontier")
        else:

            self.frontier.remove(node)

    def length(self):
        return len(self.frontier)


    @staticmethod
    def production_cost_calculation(sc_inputs, base_inputs):

        return ((sc_inputs - base_inputs) / base_inputs) * 100


    @staticmethod
    def env_cost_calculation(sc_inputs, base_inputs):

        cost = ((sc_inputs - base_inputs) / base_inputs) * 100

        return cost
    
    @staticmethod
    def combined_score_calculation(climate, eutrophication, ammonia, production_cost):
        climate_weight = .8 
        eutrophication_weight = .7
        ammonia_weight = .6
    
        env_score = (climate * climate_weight) + (eutrophication * eutrophication_weight) + (ammonia * ammonia_weight)

        production_score = abs(production_cost)

        total_score = production_score + env_score

        return total_score

class ProteinCalc:

    def __init__(self, milk_protein=None, beef_protein=None):
        self.milk_protein = milk_protein or 31
        self.beef_protein = beef_protein or 169


    def milk_protein_calculator(self, milk):
        return self.milk_protein * milk
    

    def beef_protein_calculator(self, beef):
        return self.beef_protein * beef