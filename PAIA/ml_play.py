import logging # you can use functions in logging: debug, info, warning, error, critical, log
import config
import PAIA
from demo import Demo

class MLPlay:
    def __init__(self):
        self.demo = Demo.create_demo() # create a replay buffer
        self.step_number = 0 # Count the step, not necessarily
        self.episode_number = 1 # Count the episode, not necessarily

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
        
        self.step_number += 1
        logging.info('Epispde: ' + str(self.episode_number) + ', Step: ' + str(self.step_number))

        img_suffix = str(self.episode_number) + '_' + str(self.step_number)
        logging.debug(PAIA.state_info(state, img_suffix))

        if state.event == PAIA.Event.EVENT_NONE:
            # Continue the game
            # You can decide your own action (change the following action to yours)
            action = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0)
            # You can save the step to the replay buffer (self.demo)
            self.demo.create_step(state=state, action=action)
        elif state.event == PAIA.Event.EVENT_RESTART:
            # You can do something when the game restarts by someone
            # You can decide your own action (change the following action to yours)
            action = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0)
            # You can start a new episode and save the step to the replay buffer (self.demo)
            self.demo.create_episode()
            self.demo.create_step(state=state, action=action)
        elif state.event != PAIA.Event.EVENT_NONE:
            # You can do something when the game (episode) ends
            want_to_restart = True # Uncomment if you want to restart
            # want_to_restart = False # Uncomment if you want to finish
            if self.episode_number < config.MAX_EPISODES and want_to_restart:
                # Do something when restart
                action = PAIA.create_action_object(command=PAIA.Command.COMMAND_RESTART)
                self.episode_number += 1
                self.step_number = 0
                # You can save the step to the replay buffer (self.demo)
                self.demo.create_step(state=state, action=action)
            else:
                # Do something when finish
                action = PAIA.create_action_object(command=PAIA.Command.COMMAND_FINISH)
                # You can save the step to the replay buffer (self.demo)
                self.demo.create_step(state=state, action=action)
                # You can export your replay buffer
                self.demo.export('kart.paia')
        
        logging.debug(PAIA.action_info(action))

        return action