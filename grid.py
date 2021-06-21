from typing import List, Dict
import pandas as pd
import numpy as np


class GridParam:
    def __init__(self, name, context, priority=0, data=None, start=None, stop=None, step=None, **kwargs):
        self.name = name
        self.context = context
        self.priority = priority
        self.data = data if data is not None else list(range(start, stop, step))
        self.kwargs = kwargs

    def len(self):
        return len(self.data)


class GridStaticParam:
    def __init__(self, name, context, value, pos):
        self.name = name
        self.context = context
        self.val = value
        self.pos = pos

    def __float__(self):
        return self.val

    def __repr__(self):
        return str(self.val)

    def __str__(self):
        return str(self.val)

    def simplify(self):
        return self.name, self.val

class Grid:
    def __init__(self):
        self.params: List[GridParam] = []
        self.scenarios: Dict[int, Dict] = dict()
        self.level = 0

    def add_param(self, param: GridParam):
        self.params.append(param)

    def sort_by_priority(self):
        self.params.sort(key=lambda p: p.priority)

    def generate_scenarios(self):
        self.sort_by_priority()

        df = pd.DataFrame()
        for param in self.params:
            if len(df.columns) != 0:
                df_new = pd.concat([df] * param.len(), ignore_index=True)
                param_col = np.repeat(param.data, len(df))
            else:
                df_new = pd.DataFrame()
                param_col = param.data
            df_new[param.name] = param_col
            df = df_new

        d_params = df.to_dict('index')
        grid = list()
        for pk in d_params:
            g = d_params[pk]

            for gk in g:
                context = None
                for param in self.params:
                    if param.name == gk:
                        context = param.context
                g[gk] = GridStaticParam(gk, context, g[gk], pk)
            grid.append(g)
        return grid


class GridDiff:
    def __init__(self):
        self.prev_scenario: Dict[str, GridStaticParam] = None


    def nextState(self, scenario: Dict[str, GridStaticParam]):
        diff = dict()
        for key in scenario:
            if self.prev_scenario is None or key not in self.prev_scenario \
                    or self.prev_scenario[key].val != scenario[key].val:
                diff[key] = True
            else:
                diff[key] = False

            if scenario[key].context in diff:
                diff[scenario[key].context] = diff[scenario[key].context] or diff[key]
            else:
                diff[scenario[key].context] = diff[key]

        self.prev_scenario = scenario

        return diff

