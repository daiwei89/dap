import pandas as pd
import numpy as np
import sys
from util import *

year_cutoff = 2005
train_rating_file = data_path + 'ratings_train.csv'
test_rating_file = data_path + 'ratings_test.csv'

def GenMovieMap():
  """
  Use year_cutoff to determine the test set and order the movies. Output
  movie_map.csv where first column is movieId, second column is movie_id.
  movie_id is consecutive starting from 0.
  """
  movies = pd.read_csv(data_path + 'movies.csv')
  map_pairs = []
  movie_counter = 0
  num_test = 0
  for t in movies.itertuples():
    movieId = t[1]
    year = int(t[2].rstrip()[-5:-1])
    if year < year_cutoff:
      # train movies
      map_pairs.append((movieId, movie_counter))
      movie_counter += 1
  for t in movies.itertuples():
    movieId = t[1]
    year = int(t[2].rstrip()[-5:-1])
    if year >= year_cutoff:
      map_pairs.append((movieId, movie_counter))
      movie_counter += 1
      num_test += 1
  print 'num_test movies:', num_test
  with open(trans_data_path + 'movie_map.csv', 'w') as f:
    f.write('movieId,movie_id\n')
    for k, v in map_pairs:
      f.write('%d,%d\n' % (k, v))
  print 'Wrote to ', trans_data_path + 'movie_map.csv'

def OrderMovies():
  """
  Order movies.csv by the new movie_id using MovieMap().
  """
  movies = pd.read_csv(data_path + 'movies.csv')
  movies_dict = {}  # movieId --> tuple
  for t in movies.itertuples():
    movies_dict[t[1]] = t
  # movie_id -->
  _, movieId_list = GetMovieMap()

  # Train movies followed by test movies. There are double quotes in movie
  # name in movies_all.csv.unclean that needs cleanup.
  movie_all_f = data_path + 'movies_all.csv.unclean'
  with open(movie_all_f, 'w') as f:
    f.write('movie_id,title,genres\n')
    for movie_id, movieId in enumerate(movieId_list):
      t = movies_dict[movieId]
      f.write('%d,"%s",%s\n' % (movie_id, t[2], t[3]))

  print 'Wrote to', movie_all_f

def SplitRatings():
  movie_id_map, _ = GetMovieMap()
  ratings = pd.read_csv(data_path + 'ratings.csv')
  print '# ratings:', len(ratings.index)
  num_test_ratings = 0

  rating_train_f = data_path + 'rating_train.csv'
  rating_test_f = data_path + 'rating_test.csv'
  with open(rating_train_f, 'w') as ftrain, \
  open(rating_test_f, 'w') as ftest:
    ftrain.write('user_id,movie_id,rating,timestamp\n')
    ftest.write('user_id,movie_id,rating,timestamp\n')
    for t in ratings.itertuples():
      user_id = t[1] - 1  # 0-based
      movieId = t[2]
      new_id = movie_id_map[movieId]
      if new_id >= kNumTrainMovies:
        num_test_ratings += 1
        ftest.write('%d,%d,%s,%d\n' % (user_id, new_id,
          str(t[3]), t[4]))
      else:
        ftrain.write('%d,%d,%s,%d\n' % (user_id, new_id,
          str(t[3]), t[4]))

  print 'Wrote to', rating_train_f, 'and', rating_test_f
  print '# test ratings:', num_test_ratings, ' percentage:', \
    float(num_test_ratings)/len(ratings.index) * 100


if __name__ == '__main__':
  #OrderMovies()
  #GenMovieMap()
  #SplitRatings()
  PickleCsv(data_path + 'rating_train.csv')
  PickleCsv(data_path + 'rating_test.csv')
