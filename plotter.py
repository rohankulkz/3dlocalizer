from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt


class Plotter:
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    # ax.set_xlabel('x', labelpad=20)
    # ax.set_ylabel('y', labelpad=20)
    # ax.set_zlabel('t', labelpad=20)

    def __init__(self):
        plt.show()

    def plot(self, x, y, z):
        self.ax.scatter(x, y, z)
