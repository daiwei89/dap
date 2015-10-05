import pandas as pd
import numpy as np
import sys
import math
import random
from sets import Set
from collections import defaultdict
import time

data_path = '/nfs/nas-0-16/wdai/datasets/movie_lens/20m/'
trans_data_path = '/home/wdai/dap/trans_data/'
valid_set_file = trans_data_path + 'valid_sets.csv'
movie_feature_file = trans_data_path + 'fmovie.csv'
kNumUsers = 138493
kNumTrainMovies = 17803
kNumTestMovies = 9475
kNumMovies = 27278
kNumTestRatings = 2039412
kNumTrainRatings = 17960851
kNumRatings = 20000263
kNumFolds = 5 # this many folds validation.
kLikeRating = 4 # >= rated kLikeRating are considered "like"

class Timer:
  """
  Usage:
  from wolf import Timer
  timer = Timer()
  # ... Do stuff ...
  print "Finished in", timer.elapsed(), "seconds."
  """
  def __init__(self):
    self.start_time = time.time()
    pass

  def elapsed(self):
    return time.time() - self.start_time

def Dedup(seq):
  seen = set()
  seen_add = seen.add
  return [ x for x in seq if not (x in seen or seen_add(x))]

def GetMovieMap():
  """
  Return movie_map (dict): movieId --> movie_id
  and movieId_list: [movieId0, ....] where movieId1 is the id
  corresponding to movie_id = 0
  """
  df = pd.read_csv(trans_data_path + 'movie_map.csv')
  movie_map = {}
  for t in df.itertuples():
    movie_map[t[1]] = t[2]
  movieId_list = df['movieId'].values.tolist()
  return movie_map, movieId_list

def EvalMap(predictions, user_likes_valid):
  """
  predictions: user_id --> [top_liked_valid1, ...]
  user_likes_valid: user_id --> [liked_valid1, ...]
  """
  map10 = 0
  num_eval = 0
  for user, pred in predictions.iteritems():
      if user not in user_likes_valid:
          continue
      num_eval += 1
      ap = 0
      correct = 0.0
      liked = user_likes_valid[user]
      for k in range(10):
          if pred[k] in liked:
            correct += 1
            ap += correct / (k + 1)
      ap /= 10
      map10 += ap
  #map10 /= len(predictions)
  map10 /= num_eval
  print 'eval MAP@10 on %d users' % num_eval
  return map10
  
def EvalRecall(predictions, user_likes_valid):
  """
  predictions: user_id --> [top_liked_valid1, ...]
  user_likes_valid: user_id --> [liked_valid1, ...]
  """
  recal10 = 0
  num_eval = 0
  for user, pred in predictions.iteritems():
      if user not in user_likes_valid:
          continue
      num_eval += 1
      liked = user_likes_valid[user]
      num_likes = len(liked)
      assert num_likes > 0
      num_correct = 0.0
      for c in liked:
          if c in pred:
              num_correct += 1
      recal10 += num_correct / num_likes
  recal10 /= num_eval
  print 'eval recall@10 on %d users' % num_eval
  return recal10

def GenValidationSets():
  train_ratings = pd.read_csv(data_path + 'rating_train.csv')
  assert kNumTrainRatings == len(train_ratings.index)
  movie_ratings_dict = defaultdict(int)
  for t in train_ratings.itertuples():
    movie_ratings_dict[t[2]] += 1

  movie_id = range(kNumTrainMovies)
  random.shuffle(movie_id)
  # Each line is a validation set.
  with open(valid_set_file, 'w') as f:
    movie_range = int(math.ceil(float(kNumTrainMovies) / kNumFolds))
    num_ratings_valid_total = 0
    for i in range(kNumFolds):
      num_ratings_valid = 0
      movie_begin = movie_range * i
      movie_end = kNumTrainMovies if i == kNumFolds - 1 else \
          movie_begin + movie_range
      print movie_begin, movie_end
      first_movie_id = movie_id[movie_begin]
      f.write('%d' % first_movie_id)
      num_ratings_valid += movie_ratings_dict[first_movie_id]
      for m in movie_id[(movie_begin + 1):movie_end]:
        num_ratings_valid += movie_ratings_dict[m]
        f.write(',%d' % m)
      f.write('\n')
      print 'Validation set has %f fraction ratings' % \
        (float(num_ratings_valid) / kNumTrainRatings)
      num_ratings_valid_total += num_ratings_valid
  print 'Wrote to', valid_set_file
  assert kNumTrainRatings == num_ratings_valid_total, \
    'num_ratings_valid_total: %d' % num_ratings_valid_total

def GetValidationLists():
  with open(valid_set_file) as f:
    valid_sets = []
    for line in f.read().splitlines():
      valid_sets.append(Set([int(x) for x in line.split(',')]))
  return valid_sets

def PickleCsv(filename):
  timer = Timer()
  df = pd.read_csv(filename)
  print 'csv load time:', timer.elapsed()
  pickle_path = filename + '.pickle'
  df.to_pickle(pickle_path)
  print 'Save pickle to', pickle_path 
  timer = Timer()
  df = pd.read_pickle(pickle_path)
  print 'Pickle load time', timer.elapsed()

if __name__ == '__main__':
  #GenSvdFeature()
  #GenValidationSets()
  pass
