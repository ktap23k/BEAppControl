import tensorflow as tf
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

class HandModel:
    def __init__(self) -> None:
        logger.info('Loading model....')
        self.labels = {
                0 :  'like',
                1 : 'dislike',
                2 : 'fist',
                3 : 'four',
                4 : 'call',
                5 : 'mute',
                6 : 'ok',
                7 : 'one',
                8 : 'plam',
                9 : 'peace_inverted',
                10 : 'peace',
                11 : 'rock',
                12 : 'stop_inverted',
                13 : 'stop',
                14 : 'three',
                15 : 'three2',
                16 : 'two_up_inverted',
                17 : 'two_up'
            }
        # path = os.path.abspath(os.path.dirname(__file__))+'/hand_models/hand_saved_model'
        # self.model = tf.saved_model.load(path)
        path = os.path.abspath(os.path.dirname(__file__))+'/hand_models/'
        self.model = tf.keras.models.load_model(path+'hand_modle.h5')
        self.model.load_weights(path+'hand_modle_weights.h5')

        logger.info('Loading model success!')
    
    def change_handedness(self, handedness):
        '''Check handedness, if handedness is Left return 2.0 else return 1.0'''
        if handedness.classification[0].label == 'Left':
            return 2.0
        return 1.0
        
    def handle_hand_landmarks(self, hand_landmarks, handedness, conf: float=1.0):
        '''Handel hand_landmarks'''
        
        x_min = min([landmark.x for landmark in hand_landmarks.landmark])
        y_min = min([landmark.y for landmark in hand_landmarks.landmark])
        x_max = max([landmark.x for landmark in hand_landmarks.landmark])
        y_max = max([landmark.y for landmark in hand_landmarks.landmark])
       
        
        data = [ np.array([landmark.x, landmark.y], dtype=np.float) for landmark in hand_landmarks.landmark]
        data.append(np.array([conf, self.change_handedness(handedness)], dtype=np.float))
         # coco_bbox = [x_min , y_min , (x_max - x_min) , (y_max - y_min)]
        data.append(np.array([x_min, y_min], dtype=np.float))
        data.append(np.array([x_max - x_min, y_max - y_min], dtype=np.float))
        
        data = np.array(data)
        # print(data)
        return self.predictions_hand(data)
    
    def predictions_hand(self, data: np):
        ''''''
        try:
            predictions = self.model.predict(np.reshape(data, (-1, 24, 2)))

            if np.max(predictions) > 0.5:
                return self.labels[np.argmax(predictions)], int(np.max(predictions)*100)
        except Exception as e:
            print(e)
            logger.debug(str(e))
        
        return 'None', 0
