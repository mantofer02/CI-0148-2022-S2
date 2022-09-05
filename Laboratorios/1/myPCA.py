import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as plt
import math
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


class myPCA:
    def __init__(self, df, data) -> None:
        self.df = df
        self.data = data
        self.mean_center()
        # self.get_correlation_matrix()
        # print(self.sort_eighen_matrix())
        self.plot_components()

    def mean_center(self):
        for j in range(len(self.data[0])):
            std = np.std(self.data[:, j])
            mean = np.mean(self.data[:, j])
            for i in range(len(self.data)):
                self.data[i][j] = (self.data[i][j] - mean) / std

    def get_r_matrix(self):
        data_transpose = self.data.transpose()
        n = float(len(self.data))
        return (1/n) * data_transpose.dot(self.data)

    def get_eighen_values(self):
        vector, matrix = LA.eigh(self.get_r_matrix())
        return vector, matrix

    def swap_colum(self, arr, start_index, last_index):
        arr[:, [start_index, last_index]] = arr[:, [last_index, start_index]]

    def get_sorted_eighen_matrix(self):
        vector, matrix = self.get_eighen_values()
        for i in range(len(vector)):
            min_idx = i
            for j in range(i+1, len(vector)):
                if vector[min_idx] < vector[j]:
                    min_idx = j

            vector[i], vector[min_idx] = vector[min_idx], vector[i]
            self.swap_colum(matrix, i, min_idx)
        return matrix

    def get_correlation_matrix(self):
        v = self.get_sorted_eighen_matrix()
        return self.data.dot(v)

    def plot_components(self):

        my_c = self.get_correlation_matrix()
        figure, axis = plt.subplots(2)

        print(my_c[0])

        axis[0].scatter(np.ravel(my_c[:, 0]), np.ravel(my_c[:, 1]), c=[
            'b' if i == 1 else 'r' for i in self.df['Survived']])
        axis[0].set_title('Marco\'s PCA')

        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(self.df)
        pca = PCA()
        C = pca.fit_transform(df_scaled)
        inertia = pca.explained_variance_ratio_
        V = pca.transform(np.identity(df_scaled.shape[1]))

        print("DIFERENCIA")
        print(C[0])
        input()

        axis[1].scatter(np.ravel(C[:, 0]), np.ravel(C[:, 1]), c=[
            'b' if i == 1 else 'r' for i in self.df['Survived']])
        axis[1].set_title("scikit-learn\'s PCA")

        axis[1].set_xlabel('PCA 1 (%.2f%% inertia)' % (inertia[0],))
        axis[1].set_ylabel('PCA 2 (%.2f%% inertia)' % (inertia[0],))

        plt.show()
