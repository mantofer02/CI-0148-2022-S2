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

    def plot_my_pca(self, axis):
        my_eighen_v, my_eighen_m = self.get_eighen_values()
        my_c = self.get_correlation_matrix()

        axis[0][0].scatter(np.ravel(my_c[:, 0]), np.ravel(my_c[:, 1]), c=[
            'b' if i == 1 else 'r' for i in self.df['Survived']])
        axis[0][0].set_title('Marco\'s PCA')
        axis[0][0].set_xlabel('PCA 1 (%.2f%% inertia)' %
                              (my_eighen_v[0] / len(my_eighen_m),))
        axis[0][0].set_ylabel('PCA 2 (%.2f%% inertia)' %
                              (my_eighen_v[1] / len(my_eighen_m),))

    def plot_sk_pca(self, axis):
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(self.df)
        pca = PCA()
        C = pca.fit_transform(df_scaled)
        inertia = pca.explained_variance_ratio_
        V = pca.transform(np.identity(df_scaled.shape[1]))
        axis[1][0].scatter(np.ravel(C[:, 0]), np.ravel(C[:, 1]), c=[
            'b' if i == 1 else 'r' for i in self.df['Survived']])
        axis[1][0].set_title("scikit-learn\'s PCA")

        axis[1][0].set_xlabel('PCA 1 (%.2f%% inertia)' % (inertia[0],))
        axis[1][0].set_ylabel('PCA 2 (%.2f%% inertia)' % (inertia[0],))

    def plot_sk_circle(self, axis):
        # axis[1][1].figure(figsize=(15, 15))

        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(self.df)
        pca = PCA()
        C = pca.fit_transform(df_scaled)

        axis[1][1].axhline(0, color='b')
        axis[1][1].axvline(0, color='b')
        for i in range(0, self.df.shape[1]):
            axis[1][1].arrow(0, 0, C[0][i],  # x - PC1
                             C[1][i],  # y - PC2
                             head_width=0.05, head_length=0.05)
            axis[1][1].text(C[0][i] + 0.05, C[1][i] +
                            0.05, self.df.columns.values[i])
        an = np.linspace(0, 2 * np.pi, 100)
        axis[1][1].plot(np.cos(an), np.sin(an), color="b")  # Circle
        axis[1][1].axis('equal')
        axis[1][1].set_title('Correlation Circle')

    def plot_my_circle(self, axis):

        my_eighen_v, my_eighen_m = self.get_eighen_values()
        my_c = self.get_correlation_matrix()

        axis[0][1].axhline(0, color='b')
        axis[0][1].axvline(0, color='b')
        for i in range(0, self.df.shape[1]):
            axis[0][1].arrow(0, 0, my_c[i, 0],  # x - PC1
                             my_c[i, 1],  # y - PC2
                             head_width=0.05, head_length=0.05)
            axis[0][1].text(my_c[i, 0] + 0.05, my_c[i, 1] +
                            0.05, self.df.columns.values[i])
        an = np.linspace(0, 2 * np.pi, 100)
        axis[0][1].plot(np.cos(an), np.sin(an), color="black")  # Circle
        axis[0][1].axis('equal')
        axis[0][1].set_title('Correlation Circle')

    def plot_components(self):

        figure, axis = plt.subplots(2, 2, constrained_layout=True)
        self.plot_my_pca(axis)
        self.plot_sk_pca(axis)
        self.plot_sk_circle(axis)
        self.plot_my_circle(axis)

        plt.show()
