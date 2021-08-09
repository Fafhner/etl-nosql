from typing import Dict

from util.grid import GridDiff


class Node:
    def __init__(self, name, do_):
        self.name = name
        self.do = do_


class StateMachine:
    def __init__(self, logger):
        self.preprocess_nodes: Dict[str, Node] = dict()
        self.only_once = list()
        self.flows = list()
        self.main = None
        self.ansbile_f = None
        self.logger = logger

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


    def loop(self, env, scenarios, pos=0, ml=0):
        for doo in self.only_once:
            doo.do(env, None, None, 'all')

        if pos is None:
            pos = 0

        gDiff = GridDiff()
        cnt = pos
        for scenario in scenarios[cnt:]:
            diff = gDiff.nextState(scenario)
            env_cp = env.copy()
            grid_cp = scenario.copy()
            tags = None
            for f in self.flows:
                if f['if'](env_cp, grid_cp, diff):
                    tags = '%s' % ', '.join(map(str, f['then']))
                    break
            if tags is None or (pos == cnt):
                tags = '%s' % ', '.join(map(str, self.flows[-1]['then']))
            self.logger.info(f"--- ACTIVE POS - {cnt}")

            if ml is None or ml == 0:
                self.runPreprocess(env_cp, grid_cp, diff)
            out = self.ansbile_f(env_cp, grid_cp, diff, tags)
            self.main(env_cp, grid_cp, diff)
            if ml is not None and ml == 1:
                break
            cnt += 1
