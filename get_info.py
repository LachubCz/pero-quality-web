import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import gaussian_filter

array = [ line for line in open('log.txt') if '[==============================]' in line]

validation = []
episodes = []

for i, item in enumerate(array):
    validation.append(float(item.split(" ")[10]))
    episodes.append(i)

def combined_graph(scores, episode_numbers, name, coordinates=None, linears=None, scatter=False):
    """
    method prints point graph and
    interpolation graph with gaussian filter of learning progress
    """
    if linears is not None:
        for key, value in linears.items():
            plt.plot([0, episode_numbers[-1]], [key, value], 'k-', linewidth=0.8)

    if scatter:
        plt.plot(episode_numbers, scores, 'ro', color='goldenrod', markersize=1)

    score_gf = gaussian_filter(scores, sigma=0.01791*episode_numbers[-1])

    plt.plot(episode_numbers, score_gf, color='teal', linewidth=1)

    plt.ylabel("Score")
    plt.xlabel("Episode")

    plt.savefig("./{}" .format(name), bbox_inches='tight')
    plt.clf()
    print("[Graph of learning progress visualization was saved to \"./{}\".]" .format(name))

combined_graph(validation, episodes, "log", scatter=True)