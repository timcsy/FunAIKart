import PAIA

class MLPlay:
    def __init__(self):
        pass
    def decision(self, state: PAIA.State) -> PAIA.Action:
        return PAIA.create_action_object(acceleration=False, brake=False, steering=0)