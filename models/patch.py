from typing import List
from models.pheromone import Pheromone

from loguru import logger

class Patch:
    def __init__(self):
        self.__pheromones: List[Pheromone] = []

    def count_items(self) -> int:
        return len(self.__pheromones)

    def add_pheromone(self, pheromone:Pheromone):
        self.__pheromones.append(pheromone)

    def filter_pheromones(self) -> None:
        """
        Remove all pheromones which intensity reached 0 value
        """
        logger.debug("Pheromones before")
        for p in self.__pheromones:
            logger.debug(f"Intensity: {p.get_intensity}")

        self.__pheromones = [p for p in self.__pheromones if p.get_intensity > 0]
       
        logger.debug("Pheromones after")
        for p in self.__pheromones:
            logger.debug(f"Intensity: {p.get_intensity}")

    def get_pheromones(self) -> List[Pheromone]:
        """
        Lists all the pheromones released in the cell
        """
        return self.__pheromones