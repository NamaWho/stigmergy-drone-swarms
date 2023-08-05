from models.pheromone import Pheromone

class Patch:
    def __init__(self):
        self.__pheromones = []

    def add_pheromone(self, pheromone:Pheromone):
        self.__pheromones.append(pheromone)

    def remove_pheromone(self, pheromone:Pheromone):
        self.__pheromones.remove(pheromone)