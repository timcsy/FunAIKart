import PAIA
from utils import debug_print

class MLPlay:
    def __init__(self):
        self.step = 0 # Count the step, not necessarily

    def decision(self, state: PAIA.State) -> PAIA.Action:
        '''
        Implement yor main algorithm here.
        Given a state input and make a decision to output an action
        '''
        # Implement Your Algorithm
        # Note: You can use PAIA.image_to_array() to convert
        #       state.observation.images.front.data and 
        #       state.observation.images.back.data to numpy array (range from 0 to 1)
        #       For example: img_array = PAIA.image_to_array(state.observation.images.front.data)
        self.step += 1
        debug_print('Step:', self.step)
        debug_print(PAIA.state_info(state, self.step))
        action = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0)
        if state.event == PAIA.Event.EVENT_FINISH:
            action = PAIA.create_action_object(command=PAIA.Command.COMMAND_RESTART)
            # action = PAIA.create_action_object(command=PAIA.Command.COMMAND_FINISH)
        elif state.event == PAIA.Event.EVENT_RESTART:
            # You can do something when the game restarts
            pass
        debug_print(PAIA.action_info(action))
        return action