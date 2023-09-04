import matplotlib.pyplot as plt
import numpy as np

from typing import List
from models.patch import Patch

def show_heatmap(field: List[List[Patch]]) -> None:

    num_rows = len(field)
    num_cols = len(field[0])

    heatmap_data = np.zeros((num_rows, num_cols))

    for i, row in enumerate(field):
        for j, patch in enumerate(row):
            heatmap_data[i, j] = sum(pheromone.get_intensity for pheromone in patch.get_pheromones())

    plt.clf()
    plot = plt.imshow(heatmap_data, cmap='YlOrRd', interpolation='nearest')
    plt.colorbar(plot, label="Patch Pheromones Intensity")
    plt.grid(visible=True, which='both', linestyle='-', linewidth=1, color='black')
    plt.xticks(range(len(field[0])), range(len(field[0])))
    plt.yticks(range(len(field)), range(len(field)))
    plt.gca().invert_yaxis()
    plt.title("Pheromone Heatmap")

    plt.show(block = False)

    plt.pause(1)