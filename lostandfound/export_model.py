import tensorflow as tf
from tensorflow import keras
import os

MODEL_DIR = os.path.abspath("image-classifier")
version = 2
export_path = os.path.join(MODEL_DIR,str(version))

print('export_path = {}\n'.format(export_path))

if os.path.isdir(export_path):
	print('Already saved a model, clearning up\n')
	os.rmdir(export_path)

model = tf.keras.models.load_model("items/model/items-model-2.h5")

tf.saved_model.simple_save(
	keras.backend.get_session(),
	export_path,
	inputs={'input_image':model.input},
	outputs={t.name:t for t in model.outputs})

print('\nSaved model')
