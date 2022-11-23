def lloyd(data, k, iters, type, distance):
  distance_func = euclidean_distance if distance == "euclidian" else manhattan_distance

  go = True
  epoch_c = 0

  centroids = random.choices(data, k=k)
  nearest_cluster = np.zeros(len(data))

  while go:
    for data, i in zip(data, range(len(nearest_cluster))):
      idx_centroid, min_distace = nearest_centroid(
        data, centroids, distance_func)
      pass
    pass
