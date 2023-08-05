from loguru import logger

import asyncio
import random

from models.patch import Patch
from models.swarm import Swarm
from models.droneposition import DronePosition, deg_to_m

from utils.squareperimeter import calculate_square_boundaries, is_inside_square

class Stigmergy: 

    def __init__(self, swarm:Swarm, spawn) -> None:
        self.__field = [[Patch() for _ in range(100)] for _ in range(100)]
        self.__swarm = swarm
        
        self.__boundaries = calculate_square_boundaries(deg_to_m(spawn.latitude_deg), deg_to_m(spawn.longitude_deg), 1000)
    
    async def leader_flight(self):
        """
        Leader drone of the swarm starts to fly searching for the target, thanks to the virtual sensing algorithm.
        Once reached, a pheromone is released into the related `patch` 
        """

        # Implementation: the idea is to iteratively move the drone along the x-axis and then the y-axis to minimize the discovery value
        max_discovery = 0
        logger.debug("Something??")
        
        prev_poss = await self.__swarm.positions
        prev_pos = prev_poss[0]
        self.__swarm.set_position(0, prev_pos.increment_m(-500, 0, 0))

        logger.debug("Something")
        
        for x in range(int(self.__boundaries[0][0]), int(self.__boundaries[1][0]), 10):
            discoveries = await self.__swarm.discoveries
            leader_discovery = discoveries[0]

            if leader_discovery > max_discovery:
                max_discovery = leader_discovery
                target_x = x

            prev_poss = await self.__swarm.positions
            prev_pos = prev_poss[0]
            await self.__swarm.set_position(0, prev_pos.increment_m(10, 0, 0))

        # for y in range(int(self.__boundaries[2][1]), int(self.__boundaries[0][1]), step_size):
        #     discovery = virtual_sensor(target_x, y)
        #     if discovery < min_discovery:
        #         min_discovery = discovery
        #         target_y = y


    async def start(self) -> None:
        """
        Runs the simulation to test the stigmergic algorithm
        Algorithm:
        1 - Swarm Takeoff
        2 - "Leader" drone, who can detect the target thanks to the virtual sensing algorithm, reaches the target and releases the pheromone
        3 - The whole Swarm start to fly among the working field randomly until some reaches the pheromone track.
        """

        # allow the entire swarm to takeoff
        await self.__swarm.takeoff()

        # let the leader drone arrive to the target and release the pheromone
        await self.leader_flight
