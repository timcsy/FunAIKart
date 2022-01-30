import logging # you can use functions in logging: debug, info, warning, error, critical, log
import config
import PAIA
#from demo import Demo
import cv2
import numpy as np
from dqn_model import DQN
import torch
import torch.nn as nn
import torch.optim as optim
import collections
from getkey import getkey, keys

GAMMA = 0.99
BATCH_SIZE = 32
REPLAY_SIZE = 10000
LEARNING_RATE = 1e-4
SYNC_TARGET_FRAMES = 1000
REPLAY_START_SIZE = 32

EPSILON_DECAY_LAST_FRAME = 10**4
EPSILON_START = 1.0
EPSILON_FINAL = 0.02

Experience = collections.namedtuple('Experience', field_names=['state', 'action', 'reward', 'done', 'new_state'])
class ExperienceBuffer:
    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)

    def __len__(self):
        return len(self.buffer)

    def append(self, experience):
        self.buffer.append(experience)

    def sample(self, batch_size):
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        states, actions, rewards, dones, next_states = zip(*[self.buffer[idx] for idx in indices])
        return np.array(states), np.array(actions), np.array(rewards, dtype=np.float32), \
               np.array(dones, dtype=np.uint8), np.array(next_states)



class MLPlay:
    def __init__(self):
        #self.demo = Demo.create_demo() # create a replay buffer
        global EPSILON_START
        self.step_number = 0 # Count the step, not necessarily
        self.episode_number = 1 # Count the episode, not necessarily
        self.action = 1
        self.state = [] 
        self.state_n = []
        self.device = 'cpu'
        self.net = DQN((4,28,63), 3).to(self.device)
        self.tgt_net = DQN((4,28,63), 3).to(self.device)
        self.exp_buffer = ExperienceBuffer(REPLAY_SIZE)
        self.epsilon = EPSILON_START
        self.frame_idx = 0
        self.optimizer = optim.Adam(self.net.parameters(), lr=LEARNING_RATE)
        self.cnt = 0
        self.progress = 0
        self.total_rewards = []
        self.best_mean = 0



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

        img_array = PAIA.image_to_array(state.observation.images.front.data)
        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        img_array = cv2.resize(img_array, (63, 28))
        #cv2.imshow("img",img_array)
        #cv2.waitKey(20)


        self.step_number += 1
        self.state_n.append(img_array)

        if len(self.exp_buffer)>=REPLAY_START_SIZE:
            if self.frame_idx % SYNC_TARGET_FRAMES == 0:
                self.tgt_net.load_state_dict(self.net.state_dict())
            self.optimizer.zero_grad()
            loss_t = self.calc_loss()
            loss_t.backward()
            self.optimizer.step()
            


        if self.step_number >= 44 and self.step_number % 4 == 0:
            reward = 0
            if state.observation.progress > self.progress:
                reward = (state.observation.progress - self.progress)*1000
                self.progress = state.observation.progress
            #print(reward)
            if reward < 0.1:
                self.cnt += 1
            else:
                self.cnt = 0
            exp = Experience(self.state, self.action, reward, False, self.state_n)
            self.exp_buffer.append(exp)
        
        if self.step_number % 4 == 0:
            self.state =  self.state_n.copy()
            self.state_n = []

        if self.step_number % 4 == 0:
            self.frame_idx += 1
            self.epsilon = max(EPSILON_FINAL, EPSILON_START - self.frame_idx / EPSILON_DECAY_LAST_FRAME)
            if np.random.random() < self.epsilon:
                act_v = np.random.randint(3)
            else:
                state_v = torch.tensor([self.state]).to(self.device)
                q_vals_v = self.net(state_v.float())
                _, act_v = torch.max(q_vals_v, dim=1)
            self.action = int(act_v)

        #key = getkey()
        #if key == keys.W:
        #    self.action = 1
        #elif key == keys.A:
        #    self.action = 0
        #elif key == keys.D:
        #    self.action = 2

        #logging.info('Epispde: ' + str(self.episode_number) + ', Step: ' + str(self.step_number) + ', Epsilon: ' + str(self.epsilon))

        action = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0)
        if self.episode_number < config.MAX_EPISODES and self.cnt>10:
            self.cnt = 0
            self.total_rewards.append(self.progress)
            logging.info('Epispde: ' + str(self.episode_number)+ ', Epsilon: ' + str(self.epsilon) + ', Progress: %.3f' %self.progress )
            mean_reward = np.mean(self.total_rewards[-30:])
            if self.best_mean < mean_reward:
                print("Best mean reward updated %.3f -> %.3f, model saved" % (self.best_mean, mean_reward))
                torch.save(self.net.state_dict(), "best_model.dat")
                self.best_mean = mean_reward

            action = PAIA.create_action_object(command=PAIA.Command.COMMAND_RESTART)

        elif state.event == PAIA.Event.EVENT_NONE:
            # Continue the game
            # You can decide your own action (change the following action to yours)
            if(self.action==0):
                action = PAIA.create_action_object(acceleration=False, brake=False, steering=-1.0)
            elif(self.action==1):
                action = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0)
            elif(self.action==2):
                action = PAIA.create_action_object(acceleration=False, brake=False, steering=1.0)
            #action = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0)
            # You can save the step to the replay buffer (self.demo)
            #self.demo.create_step(state=state, action=action)
        elif state.event == PAIA.Event.EVENT_RESTART:
            # You can do something when the game restarts by someone
            # You can decide your own action (change the following action to yours)
            self.step_number = 0
            self.episode_number += 1
            self.action = 1
            self.state = []
            self.state_n = []
            self.cnt = 0
            self.progress = 0
            # You can start a new episode and save the step to the replay buffer (self.demo)
            #self.demo.create_episode()
            #self.demo.create_step(state=state, action=action)
        elif state.event != PAIA.Event.EVENT_NONE:
            # You can do something when the game (episode) ends
            want_to_restart = True # Uncomment if you want to restart
            # want_to_restart = False # Uncomment if you want to finish
            if self.episode_number < config.MAX_EPISODES and want_to_restart:
                # Do something when restart
                action = PAIA.create_action_object(command=PAIA.Command.COMMAND_RESTART)
                # You can save the step to the replay buffer (self.demo)
                #self.demo.create_step(state=state, action=action)
            else:
                # Do something when finish
                action = PAIA.create_action_object(command=PAIA.Command.COMMAND_FINISH)
                # You can save the step to the replay buffer (self.demo)
                #self.demo.create_step(state=state, action=action)
                # You can export your replay buffer
                #self.demo.export('kart.paia')
            self.total_rewards.append(self.progress)
            logging.info('Epispde: ' + str(self.episode_number)+ ', Epsilon: ' + str(self.epsilon) + ', Progress: %.3f' %self.progress )
            mean_reward = np.mean(self.total_rewards[-30:])
            if self.best_mean < mean_reward:
                print("Best mean reward updated %.3f -> %.3f, model saved" % (self.best_mean, mean_reward))
                torch.save(self.net.state_dict(), "best_model.dat")
                self.best_mean = mean_reward
        
        ##logging.debug(PAIA.action_info(action))
        return action
    def calc_loss(self):
        states, actions, rewards, dones, next_states = self.exp_buffer.sample(BATCH_SIZE)

        states_v = torch.tensor(np.array( states, copy=False)).to(self.device)
        next_states_v = torch.tensor(np.array( next_states, copy=False)).to(self.device)
        actions_v = torch.tensor(actions).to(self.device)
        rewards_v = torch.tensor(rewards).to(self.device)
        done_mask = torch.BoolTensor(dones).to(self.device)

        state_action_values = self.net(states_v.float()).gather( 1, actions_v.unsqueeze(-1)).squeeze(-1)
        with torch.no_grad():
            next_state_values = self.tgt_net(next_states_v.float()).max(1)[0]
            next_state_values[done_mask] = 0.0
            next_state_values = next_state_values.detach()

        expected_state_action_values = next_state_values * GAMMA + rewards_v
        return nn.MSELoss()(state_action_values, expected_state_action_values)
