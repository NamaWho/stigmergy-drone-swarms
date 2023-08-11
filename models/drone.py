from loguru import logger
from mavsdk import System
import asyncio
import random

async def print_status_text(drone):
    """
    Print status of the drone
    """
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return

class Drone:
    def __init__(self,  sys_addr) -> None:
        self.sys_addr = sys_addr
        self.sys_port = random.randint(1000, 65535)
        self.__drone = System(port= self.sys_port)
        self.neighbours = []
        self.__drone.component_information.float_param

    async def add_neighbour(self, neigh_addr):
        neigh = Drone(neigh_addr)
        logger.debug('Adding new Drone instance')
        await neigh.connect()
        logger.debug('Added new Drone instance')
        self.neighbours.append(neigh)

    async def test_neighbour_altitude(self):
        d0 = self.neighbours[0]
        logger.debug('Ready to print altitude info')
        async for pos in d0.__drone.telemetry.position():
            print(pos.absolute_altitude_m)
            await asyncio.sleep(1)

    async def connect(self) -> None:
        """
        Connect to the Drone instance
        """
        await self.__drone.connect(system_address=f"udp://:{self.sys_addr}")

        status_text_task = asyncio.ensure_future(print_status_text(self.__drone))

        logger.debug("Waiting for drone to connect...")
        async for state in self.__drone.core.connection_state():
            if state.is_connected:
                logger.debug(f"Connected sys_addr{self.sys_addr}, sys_port{self.sys_port}!")
                break

        logger.debug("Waiting for drone to have a global position estimate...")
        async for health in self.__drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                logger.debug("Global position estimate OK")
                break

        status_text_task.cancel()
    
    def altitude(self) -> int:
        """
        Drone altitude
        """
        pos = self.__drone.telemetry.position()
        return pos.absolute_altitude_m
    
    async def arm(self):
        """
        Drone Arming
        """
        logger.debug("Arming")
        await self.__drone.action.arm()

    async def takeoff(self):
        """
        Drone Takeoff
        """
        logger.debug("Taking off")
        await self.__drone.action.takeoff()

    async def land(self):
        """
        Drone Land
        """
        logger.debug("Landing")
        await self.__drone.action.land()

    async def takeoff_and_land(self):
        """
        Drone Takeoff and Land
        """
        await self.arm()
        await self.takeoff()
        await asyncio.sleep(10)
        await self.land()