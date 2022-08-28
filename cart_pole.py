import pdb
from ssl import ALERT_DESCRIPTION_ACCESS_DENIED
import numpy as np
import time
import gym

from tensorflow import keras
from tensorflow.keras import layers


def gather_data(env):
    score_history =[]
    min_score = 50
    state_history = []
    action_history = []

    for trial in range(10000):
        print('.', end='', flush=True)

        if (trial + 1) % 100 == 0: # trial이 100번째 일때 200번재일때 만 들어가라
            print(trial + 1)
        
        state = env.reset()
        score = 0
        states = []
        actions = []

        while True:
            action = np.random.choice(2)            

            one_hot = np.zeros(2)
            one_hot[action] = 1
            
            states.append(state)
            actions.append(one_hot)

            state, reward, done, _ = env.step(action)

            score += reward
            if done:                
                break
        
        # after a play is over.
        if score > min_score:
            score_history.append(score)
            state_history += states
            action_history += actions
    
    state_history = np.array(state_history)
    action_history = np.array(action_history)

    print('# game plays: {}'.format(len(score_history)))
    print('Average: {}'.format(np.mean(score_history)))
    print('Median: {}'.format(np.median(score_history)))

    return state_history, action_history
    

def create_model():
    inputs = layers.Input(shape=(4, ))

    x = layers.Dense(128, activation='relu')(inputs)
    x = layers.Dropout(0.6)(x)

    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.6)(x)

    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(0.6)(x)

    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.6)(x)

    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.6)(x)

    
    # outputs = layers.Dense(1, activation='lnear')(x)
    outputs = layers.Dense(2, activation='softmax')(x)

    model = keras.Model(inputs=inputs, outputs=outputs)

    model.compile(
        loss='categorical_crossentropy',  # 'mse'
        optimizer='adam',
        metrics=['accuracy']

    )
    return model


if __name__ =='__main__':
    env = gym.make('CartPole-v1')   

    print('Gathering data...')
    state_history, action_history = gather_data(env)

    print('Creating a deep-learning model...')
    model = create_model()

    # print(model.summary())

    print('Training the AI model...')

    model.fit(state_history, action_history, epochs=5)

    print('Test AI')

    for trial in range(100):
        state = env.reset()
        running_reward = 0  

        while True:
            env.render()

            # action = np.random.choice(2)

            predicted = model.predict(state.reshape(1,-1))
            action = np.argmax(predicted)

            state, reward, done, _ = env.step(action)
            running_reward += reward

            if done:
                break

        
        print('Final reward sum: ', running_reward)

    