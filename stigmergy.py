from loguru import logger

import asyncio
import random

from models.patch import Patch
from models.swarm import Swarm
from models.droneposition import DronePosition, deg_to_m

from utils.squareperimeter import calculate_square_boundaries, is_inside_square

class Stigmergy: 

    def __init__(self, spawn:DronePosition):
        self.__field = [[Patch() for _ in range(100)] for _ in range(100)]
        self.__boundaries = calculate_square_boundaries(deg_to_m(spawn.latitude_deg), deg_to_m(spawn.longitude_deg), 1000)

    def start_simulation(self):
        """
        Runs the whole simulation to test the stigmergic algorithm
        """
        1