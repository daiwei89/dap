import pandas as pd
import numpy as np
import sys
from collections import defaultdict
from util import *

def UserLikes(valid_list):
  """
  Returns two maps:
  user_likes_train = user_id --> [no_valid_movie_id1, ...]
  user_likes_valid = user_id --> [valid_movie_id1, ...]
  where movie_id1... are movies rated above kLikeRating
  Exclude ratings on movies in valid_list
  """
  user_likes_train = defaultdict(list)
  user_likes_valid = defaultdict(list)
  train_ratings = pd.read_csv(data_path + 'rating_train.csv')
  for t in train_ratings.itertuples():
    user_id = t[1]
    movie_id = t[2]
    rating = t[3]
    if t[3] >= kLikeRating:
      if movie_id not in valid_list:
        user_likes_train[user_id].append(movie_id)
      else:
        user_likes_valid[user_id].append(movie_id)
  num_users_rerate = 0
  for u in user_likes_train:
    u_likes = user_likes_train[u]
    num_items = len(u_likes)
    user_likes_train[u] = Dedup(u_likes)
    if num_items != user_likes_train[u]:
      num_users_rerate += 1
  print '%f users rerated in train set' % \
    (float(num_users_rerate)/len(user_likes_train))

  num_users_rerate = 0
  for u in user_likes_valid:
    u_likes = user_likes_valid[u]
    num_items = len(u_likes)
    user_likes_valid[u] = Dedup(u_likes)
    if num_items != user_likes_valid[u]:
      num_users_rerate += 1
  print '%f users rerated in train set' % \
    (float(num_users_rerate)/len(user_likes_train))

  return user_likes_train, user_likes_valid

def CosineSim(valid_list):
  """
  valid_list is a list of movie_id that's validation set
  """
  #train_ratings = pd.read_csv(data_path + 'rating_train.csv')
  user_likes_train, user_likes_valid = UserLikes(valid_list)
  print 'kNumUsers:', kNumUsers, '# users who liked at least 1 movie in', \
    'train_set - valid_list', len(user_likes_train)
  movies = pd.read_csv(trans_data_path + 'fmovie_decade.csv')
  train_movies = movies.iloc[:kNumTrainMovies]
  train_movies.drop('movie_id', axis=1, inplace=True)
  movies_mat = train_movies.values

  # valid_movie_mat: [m x k] (m validation movies)
  valid_movie_mat = np.matrix([movies_mat[i] for i in valid_list])
  # prediction: user_id --> [liked movies]
  prediction = {}
  for u, likes in user_likes_train.iteritems():
    # user_profile: [n x k] (n likes and k-dim movie feature)
    user_profile = np.matrix([movies_mat[i] for i in likes])
    # scores: [n x m]
    scores = np.dot(user_profile, np.transpose(valid_movie_mat))
    # sort vertically, order n scores for each validation movie (smallest at
    # the first row).
    scores.sort(axis=0)
    # scale_vec: [small --> large scale]
    scale_vec = [pow(0.8,i) for i in range(len(likes))]
    scale_vec.reverse()

    scores = np.dot(scale_vec, scores).tolist()
    top_k = [valid_list[j] for j in np.argsort(scores)[-10:][::-1]]
    prediction[u] = top_k

  map10 = EvalMap(predictions, user_likes_valid)
  recall10 = EvalRecall(predictions, user_likes_valid)
  return map10, recall10

if __name__ == '__main__':
  valid_lists = GetValidationLists()
  map_vals = []
  recalls = []
  for v in valid_lists:
    map_val, recall = CosineSim(v)
    map_vals.append(map_val)
    recalls.append(recall)
  print 'avg map10', reduce(lambda x, y: x + y, map_vals) / len(map_vals)
  print 'avg recall', reduce(lambda x, y: x + y, recalls) / len(recalls)
