import pandas as pd
import numpy as np
import sys
from util import *
import math
import random


def GenSvdFeature():
  train_ratings = pd.read_csv(data_path + 'rating_train.csv')
  movies = pd.read_csv(trans_data_path + 'fmovie_decade.csv')

  svd_train_file = trans_data_path + 'train.svd'
  svd_test_file = trans_data_path + 'test.svd'


if __name__ == '__main__':
  #GenSvdFeature()
  GenValidationSets()
