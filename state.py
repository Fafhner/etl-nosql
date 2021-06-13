class State:
    pass


class StateMachine:
    def __init__(self, links):
        """

        :param links:
        {
         state0: [state1, state2],
         state1: [state2, state3],
         state2: [state4]
         }
        """
        self.links = links
        self.state = None
        self.prev_state = None
        self.history = []

    def updateToState(self, next_state):
        if next_state in self.links[self.state]:
            if self.prev_state is not None:
                self.history.append(self.prev_state)
            self.prev_state = self.state
            self.state = next_state
        else:
            raise Exception(f"Unable to move to state: {next_state} from state: {self.state}")



    def saveStateAsDict(self):
        d = {
            "links": self.links,
            "state": self.state,
            "prev_state": self.prev_state,
            "history": self.history
        }
        return d
