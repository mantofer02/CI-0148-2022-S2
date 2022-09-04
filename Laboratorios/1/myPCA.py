import numpy as np
from numpy import linalg as LA


class myPCA:
    def __init__(self, data) -> None:
        self.data = data
        self.mean_center()
        self.get_correlation_matrix()

    def mean_center(self):
        for j in range(len(self.data[0])):
            std = np.std(self.data[:, j])
            mean = np.mean(self.data[:, j])
            for i in range(len(self.data)):
                self.data[i][j] = (self.data[i][j] - mean) / std

    def get_correlation_matrix(self):
        data_transpose = self.data.transpose()
        n = float(len(self.data))
        return (1/n) * data_transpose.dot(self.data)
