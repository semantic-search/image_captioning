from flask import Flask, render_template, request
import werkzeug
from werkzeug import secure_filename
import os
import tensorflow as tf
from config import Config
from model import CaptionGenerator
from dataset import prepare_train_data, prepare_eval_data, prepare_test_data
import csv
import nltk
import time
from flask_restplus import Resource, Api, reqparse
from werkzeug.datastructures import FileStorage
nltk.download('punkt')
sess = tf.InteractiveSession()
config = Config()
config.phase = 'test'
config.train_cnn =  True
config.beam_size = 3
model = CaptionGenerator(config)
model.load(sess, 'model/289999.npy')
cwd = os.getcwd()
app = Flask(__name__)
api = Api(app, version='1.0', title='Image Caption',
    description='Show and tell image caption',
)
ns = api.namespace('', description='Run inference for image captioning on your image')
app.config['UPLOAD_FOLDER'] = 'test/images'
parser = api.parser()
parser.add_argument('in_files', type=werkzeug.datastructures.FileStorage, location='files')
upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)
@ns.route('/upload/')
@ns.expect(upload_parser)
class Upload(Resource):
   def post(self):
      args = upload_parser.parse_args()
      f = args['file']
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
      data, vocabulary = prepare_test_data(config)
      a = time.time()
      model.test(sess, data, vocabulary)
      b = time.time()
      print(a-b)
      reader = csv.DictReader(open('test/results.csv'))
      dictobj = next(reader) 
      response_dict = {
         "caption" : dictobj["caption"],
         "prob" : dictobj["prob"]
      }
      os.remove(app.config['UPLOAD_FOLDER']+"/"+f.filename)
      os.remove('test/results.csv')
      return response_dict
		
if __name__ == '__main__':
   app.run(debug=True)
