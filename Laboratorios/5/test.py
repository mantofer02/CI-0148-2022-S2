def plot_tensor(tensor, perm=None):
    if perm == None:
        perm = (1, 2, 0)
    plt.figure()
    plt.imshow(tensor.permute(perm).numpy().astype(np.uint8))
    plt.show()
