import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

model = keras.models.load_model('./NN/normal_model.h5')
# same with model(!)
# characters = ['f', 'q', '0', '9', 'e', 'm', 'd', 'a', '4', 'z', '8', 'n', 's', '5', 'g', 'k', 'x', 'u', '7', 'l', 'b', 'i', 'c', 'o', 'v', '.', 'j', 'h', '@', 'p', 'r', '2', 'y', 'w', '1', '6', 't', '3']
characters = [' ', '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '@', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

char_to_num = layers.experimental.preprocessing.StringLookup(
    vocabulary=list(characters), num_oov_indices=0, mask_token=None
)

num_to_char = layers.experimental.preprocessing.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True
)

max_length = 3

def decode_batch_predictions(pred):
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    # Use greedy search. For complex tasks, you can use beam search
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][
        :, :max_length
    ]
    # Iterate over the results and get back the text
    output_text = []
    for res in results:
        res = tf.strings.reduce_join(num_to_char(res)).numpy().decode("utf-8")
        output_text.append(res)
    return output_text

def translate(img_path):
    img = tf.io.read_file(img_path)
    img = tf.io.decode_png(img, channels=1)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = tf.image.resize(img, [100, 100])
    img = tf.transpose(img, perm=[1, 0, 2])
    result = model.predict(np.array([img]))
    return decode_batch_predictions(result)[0].replace('[UNK]', '').replace(' ', '')

