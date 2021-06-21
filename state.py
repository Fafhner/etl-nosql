from typing import Dict

from grid import GridDiff


class Node:
    def __init__(self, name, do_):
        self.name = name
        self.do = do_


class StateMachine:
    def __init__(self):
        self.preprocess_nodes: Dict[str, Node] = dict()
        self.only_once = list()
        self.flows = list()
        self.main = None
        self.ansbile_f = None

    def addNodes(self, nodes: list):
        for node in nodes:
            self.preprocess_nodes[node.name] = node

    def setDoOnlyOnce(self, oo):
        self.only_once = oo

    def setMain(self, main):
        self.main = main

    def setFlowTree(self, flows):
        self.flows = flows

    def runPreprocess(self, env, grid, diff):
        for pk in self.preprocess_nodes:
            self.preprocess_nodes[pk].do(env, grid, diff)


    def loop(self, env, scenarios):
        for doo in self.only_once:
            doo.do(env, None, None, 'all')

        gDiff = GridDiff()
        for scenario in scenarios:

            diff = gDiff.nextState(scenario)
            env_cp = env.copy()
            grid_cp = scenario.copy()
            tags = None
            for f in self.flows:
                if f['if'](env_cp, grid_cp, diff):
                    tags = '%s' % ', '.join(map(str, f['then']))
                    break

            self.runPreprocess(env_cp, grid_cp, diff)
            self.ansbile_f(env_cp, grid_cp, diff, tags)

            self.main(env_cp, grid_cp, diff)
