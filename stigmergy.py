from loguru import logger

import asyncio
import random
import itertools
from mavsdk import System
from typing import List

from models.patch import Patch
from models.swarm import Swarm
from models.pheromone import Pheromone
from models.droneposition import DronePosition, deg_to_m, m_to_deg

from utils.stigmergy.squareperimeter import calculate_square_boundaries
from utils.stigmergy.patch import get_patch_coords
from utils.stigmergy.heatmap import show_heatmap

class Stigmergy: 

    def __init__(self, swarm:Swarm, spawn:DronePosition, target:DronePosition) -> None:
        self.__field: List[List[Patch]] = [[Patch() for _ in range(20)] for _ in range(20)]
        self.__swarm = swarm
        self.__boundaries = calculate_square_boundaries(deg_to_m(spawn.latitude_deg), deg_to_m(spawn.longitude_deg), 100)
        logger.debug(f"Boundaries: {self.__boundaries}")
        self.__virtual_target = target

    async def random_swarm_movement(self, index, drone:System) -> None:
        drone_pos = DronePosition(0,0,0)

        while True:

            # Update the position based on random velocity
            new_latitude = self.__boundaries[0][0] + random.randint(0, 99)
            new_longitude = self.__boundaries[2][1] + random.randint(0, 99)

            drone_pos.latitude_deg = m_to_deg(new_latitude)
            drone_pos.longitude_deg = m_to_deg(new_longitude)
            drone_pos.absolute_altitude_m = 490

            # Move the drone to the new position
            # await drone.action.goto_location(new_latitude, new_longitude, 0, 0)
            await self.__swarm.set_position(index, drone_pos)
            await asyncio.sleep(10)

    def release_pheromone(self, target:DronePosition):
        pheromone = Pheromone()

        x_index, y_index = get_patch_coords(self.__boundaries[0][0], self.__boundaries[2][1], 100, 20, target)
        
        patch = self.__field[x_index][y_index]
        patch.add_pheromone(pheromone)

        logger.success(f"Released pheromone @{x_index, y_index}")

        show_heatmap(self.__field)


    async def pheromone_routine(self) -> None:

        while True:
            # check drone positions in order to detect pheromone tracks
            drone_positions = await self.__swarm.positions
            drone_patches = []

            drone_patches = [get_patch_coords(self.__boundaries[0][0], self.__boundaries[2][1], 100, 20, d) for d in drone_positions]

            # logger.debug(drone_patches)
            
            for i, p in enumerate(drone_patches):
                if self.__field[p[0]][p[1]].count_items() > 0:
                    self.release_pheromone(drone_positions[i])

            # update pheromone intensity due to evaporation
            for row in self.__field:
                for patch in row:
                    pheromones = patch.get_pheromones()

                    for item in pheromones:
                        is_active = item.tick()
                        
                        if(not is_active):
                            logger.info("Removing vanished PHEROMONE")
                            patch.filter_pheromones()
                            show_heatmap(self.__field)

            await asyncio.sleep(1)

    async def maximize_discovery(self, offset_x=0, offset_y=0, interval=1) -> None:
        leader = self.__swarm.get_leader()
        
        max_discovery = 0
        max_position = DronePosition(0,0,0)
        # prev_position = DronePosition(0,0,0)

        prev_poss = await self.__swarm.positions
        prev_pos = prev_poss[0]
        await leader.action.set_maximum_speed(5)
        await self.__swarm.set_position(0, prev_pos.increment_m(-offset_x, -offset_y, 0))
        await asyncio.sleep(30*interval)
        await leader.action.set_maximum_speed(1.8)
        await self.__swarm.set_position(0, prev_pos.increment_m(offset_x, offset_y, 0))

        while True:
            position = await anext(leader.telemetry.position())

            discoveries = await self.__swarm.discoveries
            leader_discovery = discoveries[0]

            if leader_discovery >= max_discovery:
                logger.debug(f"NEW Max discovery: {leader_discovery}")
                max_discovery = leader_discovery
                max_position = DronePosition.from_mavsdk_position(position)
            else: 
                logger.debug("Reached the highest discovery value")
                await self.__swarm.set_position(0, max_position)
                await asyncio.sleep(10)
                break

            # prev_position.from_mavsdk_position(position)
            await asyncio.sleep(interval)

    async def leader_flight(self) -> None:
        """
        Leader drone of the swarm starts to fly searching for the target, thanks to the virtual sensing algorithm.
        Once reached, a pheromone is released into the related `patch` 
        """
        leader = self.__swarm.get_leader()
        # await leader.action.set_maximum_speed(10)
        await self.__swarm.set_position(0, self.__virtual_target)
        await asyncio.sleep(10)

        logger.info("Target FOUND. Releasing Pheromone")
        self.release_pheromone(self.__virtual_target)

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
        await asyncio.sleep(10)

        # let the leader drone arrive to the target and release the pheromone
        await self.leader_flight()

        # start the random swarm movement for each drone
        # start the pheromone sensing and evaporation routine
        tasks = [self.random_swarm_movement(i, drone) for i, drone in enumerate(self.__swarm.get_drones())]
        tasks.append(self.pheromone_routine())

        # start the pheromone sensing and evaporation routine
        # while True:
        #     await self.pheromone_routine()
        #     await asyncio.sleep(1)

        await asyncio.gather(*tasks)