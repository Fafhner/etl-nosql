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
        params = self.params

        df = pd.DataFrame()
        for param in params:
            if len(df.columns) != 0:
                df_new = pd.concat([df] * param.len(), ignore_index=True)
                param_col = np.repeat(param.data, len(df))
            else:
                df_new = pd.DataFrame()
                param_col = param.data
            df_new[param.name] = param_col
            df = df_new

        return df.to_dict('index')


class GridDiff:
    def __init__(self):
        self.prev_scenario = None

    def nextState(self, scenario: dict):
        diff = dict()
        for key in scenario:
            if self.prev_scenario is None or key not in self.prev_scenario or self.prev_scenario[key] != scenario[key] :
                diff[key] = True
            else:
                diff[key] = False

        self.prev_scenario = scenario

        return diff
