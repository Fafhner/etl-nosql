from typing import Dict

from grid import GridDiff

from run import scenario_diff


class Node:
    def __init__(self, name, do_):
        self.name = name
        self.do = do_

class StateMachine:
    def __init__(self):
        self.nodes: Dict[str, Node] = dict()
        self.only_once = list()
        self.flows = list()
        self.main = None

    def addNodes(self, nodes: list):
        for node in nodes:
            self.nodes[node.name] = node

    def setDoOnlyOnce(self, oo):
        self.only_once = oo

    def setMain(self, main):
        self.main = main

    def setFlowTree(self, flows):
        self.flows = flows

    def runPreprocess(self, env, grid, diff, flow):
        for f in flow['then']:
            n = self.nodes[f]
            n.do(env, grid, diff)


    def loop(self, env, scenarios):
        for doo in self.only_once:
            doo.do(env, None, None)

        gDiff = GridDiff()
        for scenario in scenarios:

            diff = gDiff.nextState(scenario)
            env_cp = env.copy()
            grid_cp = scenario.copy()
            flow = None
            for f in self.flows:
                if f['if'](env_cp, grid_cp, diff):
                    flow = f
                    break

            self.runPreprocess(env_cp, grid_cp, diff, flow)

            self.main(env_cp, grid_cp, diff)
