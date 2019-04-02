import argparse
import json
import os

import model1
import tensorflow as tf

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
      '--model_dir',
      help='location to write checkpoints and export models',
      required=True
  )
    parser.add_argument(
      '--data_dir',
    help='location of train and test files',
    required=True
  )
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
    
    args = parser.parse_args()
    hparams = args.__dict__
    data_dir = hparams.pop('data_dir')
    model_dir = hparams.pop('model_dir')
    model1.train(data_dir, model_dir)
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
