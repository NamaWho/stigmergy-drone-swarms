from typing import List
from models.pheromone import Pheromone

class Patch:
    def __init__(self):
        self.__pheromones: List[Pheromone] = []

    def count_items(self) -> int:
        """
        Return number of pheromones released in the patch
        """
        return len(self.__pheromones)

    def add_pheromone(self, pheromone:Pheromone):
        """
        Add a new pheromone in the patch
        """
        self.__pheromones.append(pheromone)

    def filter_pheromones(self) -> None:
        """
        Remove all pheromones which intensity reached 0 value
        """
        self.__pheromones = [p for p in self.__pheromones if p.get_intensity > 0]

    def get_pheromones(self) -> List[Pheromone]:
        """
        Lists all the pheromones released in the cell
        """
        return self.__pheromones