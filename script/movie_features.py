import pandas as pd
import numpy as np
import sys
from util import *


def GenerateMovieFeature():
  """
  data_path + movies_all.csv has movie_id such that train movies are followed
  by test, starting from 0.
  """
  movies = pd.read_csv(data_path + 'movies_all.csv')
  genre_dict = {}
  num_genres = 0
  genre_list = []
  for t in movies['genres']:
    for g in t.split('|'):
      if g not in genre_dict and g != "(no genres listed)":
        genre_dict[g] = num_genres
        genre_list.append(g)
        num_genres += 1

  print '# genres:', num_genres

  header = 'movie_id,year'
  for g in genre_list:
    header += ',genre' + g
  with open(movie_feature_file, 'w') as f:
    f.write(header + '\n')
    for t in movies.itertuples():
      print t[0]
      year = int(t[2].rstrip()[-5:-1])
      assert year > 1800, 'row %d has year %d' % ((t[0] + 1), year)
      assert year < 2016, 'row %d has year %d' % ((t[0] + 1), year)
      f.write('%d,%d' % (t[1], year))

      genre_vec = np.zeros((num_genres,1))
      for g in t[3].split('|'):
        if g != "(no genres listed)":
          genre_vec[genre_dict[g]] = 1
      for i in xrange(genre_vec.shape[0]):
        f.write(',%d' % genre_vec[i])
      f.write('\n')
  print 'Wrote to', movie_feature_file

def GenerateDecadeWiseMovieFeature():
  movies = pd.read_csv(movie_feature_file)
  min_decade = 1890
  # max out at 2010 (count 201X movies as 2000 bucket)
  num_decades = (2010 - min_decade) / 10
  curr_cols = movies.columns.tolist()
  new_cols = []
  for i in range(num_decades):
    decade_begin = min_decade + i * 10
    col_name = str(decade_begin) + '_decade'
    new_cols.append(col_name)
    movies[col_name] = 0
  # reorder the columns to have decade be column 2~ (column 1 is movie_id)
  movies = movies[curr_cols[:1] + new_cols + curr_cols[1:]]

  for i, y in enumerate(movies['year']):
    # Make 201X movies into the same category as 2000 since training set has
    # only movie up to 2004.
    decade_idx = (min(y, 2009) - min_decade) / 10
    movies.set_value(i, new_cols[decade_idx], 1)
  movies.drop('year', axis=1, inplace = True)
  print movies.columns

  output_file = trans_data_path + 'fmovie_decade.csv'
  movies.to_csv(output_file, index = False)
  print 'Output to', output_file

if __name__ == '__main__':
  #GenerateMovieFeature()
  GenerateDecadeWiseMovieFeature()
