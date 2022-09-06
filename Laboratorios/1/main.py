import pca_utils
from myPCA import myPCA


def main():
    titanicPCA = myPCA(pca_utils.preprocess_df(pca_utils.load_df(
        'titanic.csv')), pca_utils.load_data())

    titanicPCA.run()


if __name__ == "__main__":
    main()
