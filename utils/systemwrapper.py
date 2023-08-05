from loguru import logger
from mavsdk import System
import random

class SystemWrapper:
    """
    Offers simpler APIs to interact with System instances.
    It can create a System instance and connect to it.
    """

    @logger.catch
    def __init__(self,
                 system_addr:int) -> None:
        """
        Creates a System instance at the given address
        
        Args:
            system_addr (int): System address (drone)
        """
        self.system_addr = system_addr
        self.server_port = random.randint(1000, 65535)

        logger.debug(f"Creating System: system_addr={self.system_addr}, server_port={self.server_port}")
        self.system = System(port=self.server_port)
    
    @logger.catch
    async def connect(self) -> System:
        """
        Connects to a System instance (drone).
        In order to reduce complexity, from the extern is already accessible a connected Drone.

        Returns:
            Already connected system instance
        """
        logger.debug(f"Connecting to system@{self.system_addr}")
        await self.system.connect(f"udp://:{self.system_addr}")
        async for state in self.system.core.connection_state():
            if state.is_connected:
                logger.debug("Connection completed")
                break

        logger.debug("Waiting for drone to have a global position estimate...")
        async for health in self.system.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                logger.debug("Global position estimate OK")
                break
        return self.system
    