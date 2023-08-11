import asyncio
import random
import itertools

from typing import List
from loguru import logger

from models.patch import Patch
from models.swarm import Swarm
from models.pheromone import Pheromone
from models.droneposition import DronePosition, deg_to_m, m_to_deg

from utils.stigmergy.squareperimeter import calculate_square_boundaries
from utils.stigmergy.patch import get_patch_coords
from utils.stigmergy.heatmap import show_heatmap
from utils.stigmergy.virtualtarget import get_virtual_target

class Stigmergy:
    """
    Class defined to run drones swarm simulation based on stigmergic algorithm. 
    It performs a basic recruitment algorithm reproducing the behaviour of natural species such as ants.
    The algorithm leverages the concept of Pheromone in order to signal a target on the flying area to the entire drones swarm. 
    """

    def __init__(self, swarm:Swarm, spawn:DronePosition) -> None:
        """
        __field: quantized square map, divided in patches
        __swarm: drone swarm associated with the simulation
        __boundaries: physical boundaries of the map (calculated considering the drones spawn position as the center of the square)
        """
        self.__field: List[List[Patch]] = [[Patch() for _ in range(20)] for _ in range(20)]
        self.__swarm = swarm
        self.__boundaries = calculate_square_boundaries(deg_to_m(spawn.latitude_deg), deg_to_m(spawn.longitude_deg), 100)

    def hold_position(self, index:int) -> bool:
        """
        Function to control if a drone has to maintain its position on a patch where it just released a new pheromone.
        Returns:
        - True if it has to maintain it position 
        """
        for row in self.__field:
            for patch in row:
                for pheromone in patch.get_pheromones():
                    if pheromone.released_by == index:
                        logger.info(f"[Vehicle {index+1}] holding position on the pheromone track")
                        return True
        
        return False

    async def random_swarm_movement(self, index) -> None:
        """
        Handle the randomic movement of the drones swarm across the map. 
        Each instance of the function is related to a single drone, identified by `index` 
        """
        drone_pos = DronePosition(0,0,0)

        while True:
            # check if currently the drone has already reached a pheromone track and has still to hold its position
            if not self.hold_position(index):
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
            else:
                await asyncio.sleep(2)

    def release_pheromone(self, target:DronePosition, index:int=0):
        """
        Release a new pheromone on the given `target` position.
        Assign the new pheromone released to a specific drone identified by its `index`.
        This prevents the same drone to release multiple pheromones on the same patch while scanning for pheromones.
        """
        pheromone = Pheromone()
        pheromone.released_by = index

        x_index, y_index = get_patch_coords(self.__boundaries[0][0], self.__boundaries[2][1], 100, 20, target)
        
        patch = self.__field[x_index][y_index]
        patch.add_pheromone(pheromone)

        logger.success(f"Released pheromone @{x_index, y_index}")

        show_heatmap(self.__field)

    async def pheromone_routine(self) -> None:
        """
        Routine that triggers every 1 second. Tasks:
        1) Check current drone position to handle pheromone releases across the map
        2) Handle pheromone evaporation 
        """

        while True:
            # check drone positions in order to detect pheromone tracks
            drone_positions = await self.__swarm.positions
            drone_patches = []

            drone_patches = [get_patch_coords(self.__boundaries[0][0], self.__boundaries[2][1], 100, 20, d) for d in drone_positions]
            
            for i, p in itertools.islice(enumerate(drone_patches), 1, None):
                if self.__field[p[0]][p[1]].count_items() > 0:

                    release_approved = True
                    pheromones = self.__field[p[0]][p[1]].get_pheromones()
                    for pheromone in pheromones:
                        if pheromone.released_by == i:
                            release_approved = False

                    if release_approved:
                        logger.success(f"[Vehicle {i+1}] discovered a pheromone track at {p}. Holding position.")
                        # release pheromone on the target patch
                        self.release_pheromone(drone_positions[i], i)

                        # send fly command to the drone to reach the target position and hold
                        await self.__swarm.set_position(i, drone_positions[i])

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

    async def leader_flight(self) -> None:
        """
        Leader drone of the swarm starts to fly searching for the target, thanks to the virtual sensing algorithm.
        Once reached, a pheromone is released into the related `patch` 
        """

        while True:
            virtual_target = get_virtual_target(self.__boundaries[0][0], self.__boundaries[2][1], 100)

            await self.__swarm.set_position(0, virtual_target)
            await asyncio.sleep(7)

            logger.info("[LEADER DRONE] Target reached")
            self.release_pheromone(virtual_target)


    async def start(self) -> None:
        """
        Runs the simulation to test the stigmergic algorithm
        Algorithm:
        1 - Swarm Takeoff
        2.1 - "Leader" drone, who can detect the target thanks to the virtual sensing algorithm, starts reaching targets and releasing pheromones
        2.2 - The whole Swarm start to fly among the working field randomly until some reaches a pheromone track
        2.3 - A routine is launched every 1 second to handle pheromones evaporation and check drones position, sending instructions if a drone flies over a pheromone track 
        """

        # allow the entire swarm to takeoff
        await self.__swarm.takeoff()
        await asyncio.sleep(10)

        # start the random swarm movement for each drone except Leader
        # start the leader drone movement
        # start the pheromone sensing and evaporation routine
        tasks = [self.random_swarm_movement(i) for i in range(1, len(self.__swarm.get_drones()))]
        tasks.append(self.leader_flight())
        tasks.append(self.pheromone_routine())

        await asyncio.gather(*tasks)