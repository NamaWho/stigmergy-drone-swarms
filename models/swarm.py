from loguru import logger
from pprint import pprint
from mavsdk import System
import asyncio
from typing import List, Callable
from utils.systemwrapper import SystemWrapper
from models.droneposition import DronePosition

class Swarm:
    """
    Creates a drones swarm composed by `drones_number` vehicles at the given addresses or incremental addresses

    Args:
        drones_number (int): number of drones composing the swarm
        drones_addrs (List[int], optional): drone addresses
            Defaults to None.
    Attributes:

    Raises:
        ValueError: drones_number must coincide with the number of drone addresses
    """

    next_drone_address = 14540 
    def __init__(self,
                drones_number:int,
                drones_addrs:List[int]=None) -> None:
        self.__drones_number = drones_number
        self.__positions = []
        self.__drones:List[System] = []

        if drones_addrs == None:
            self.drones_addrs = []
            for i in range(drones_number):
                self.drones_addrs.append(Swarm.next_drone_address)
                Swarm.next_drone_address += 1
        elif drones_number != len(drones_addrs):
            raise ValueError
        else:
            self.drones_addrs = drones_addrs
        logger.info(f"Creating swarm with {self.__drones_number} drones at {self.drones_addrs}")


    async def connect(self):
        """
        Connects to every drone of the swarm simultaneously
        """
        logger.info("Connecting to drones...")
        for a in self.drones_addrs:
            logger.info(f"Connecting to drone@{a}...")
            sysW = SystemWrapper(a)
            drone = await sysW.connect()
            logger.info(f"Connection to drone@{a} completed")
            self.__drones.append(drone)


    async def check_system_connections(self) -> bool:
        """
        Check if all the drones [System] are connected to the base station
        """
        for system in self.__drones:
            async for state in system.core.connection_state():
                if state.is_connected:
                    logger.debug("Drone is connected.")
                    break
                else:
                    logger.debug("Drone is not connected.")
                    return False
        return True

    async def takeoff(self):
        """
        Sends `takeoff` command to each drone of the swarm.
        """

        # assert that all the drones are connected
        ready_for_takeoff = 0
        while not ready_for_takeoff:
            ready_for_takeoff = await self.check_system_connections()

        logger.info("Taking off...")
        for d in self.__drones:
            await d.action.arm()
            await d.action.takeoff()
            await d.action.set_maximum_speed(10)
        logger.info("Takeoff completed")

    async def land(self):
        """
        Sends `land` command to each drone of the swarm.
        """
        logger.info("Landing...")
        for d in self.__drones:
            await d.action.land()
        logger.info("Landing completed")

    @property
    async def positions(self) -> List[DronePosition]:
        """
        Retrieves drones positions

        Returns:
            List[DronePosition]: Current position of each drone
        """
        self.__positions = []
        for d in self.__drones:
            p = await anext(d.telemetry.position())
            pos = DronePosition.from_mavsdk_position(p)
            self.__positions.append(pos)

        return self.__positions
    
    async def set_position(self, index, target_position:DronePosition):
        """
        Sets a new position (`target_position`) for the drone identified by its index
        """
        try:
            prev_pos = self.__positions[index]
            drone = self.__drones[index]
        except IndexError:
            return
        
        logger.info(f"Moving drone@{self.drones_addrs[index]}")
        await drone.action.goto_location(*target_position.to_goto_location(prev_pos))
    
    async def set_positions(self, target_positions:List[DronePosition]):
        """
        Sets a new position (`target_position`) for each drone

        Args:
            target_positions (List[DronePosition]): List of target position 
        """
        prev_pos = await self.positions
        print(prev_pos)
        for n, d in enumerate(self.__drones):
            pos = target_positions[n]
            logger.info(f"Moving drone@{self.drones_addrs[n]} to {pos}")
            await d.action.goto_location(*pos.to_goto_location(prev_pos[n]))
    
    def get_leader(self) -> System:
        """
        Get the first drone of the swarm, which will be called "Leader"
        """
        return self.__drones[0]
    
    def get_drones(self) -> List[System]:
        """
        Get the list of all the drones of the swarm
        """
        return self.__drones