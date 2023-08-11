# --- DEPENDENCIES ---
import asyncio
import random
import math

from loguru import logger

from models.swarm import Swarm
from models.droneposition import DronePosition
from stigmergy import Stigmergy
# --------------------

# --- GLOBAL VARIABLES ---
VIRTUAL_TARGET = None   # virtual target generated on working field
# ------------------------

# --- FUNCTIONS ---

async def create_virtual_target(swarm:Swarm, max_radius) -> DronePosition:
    """
    Creates a random virtual target inside the specified working field.
    For academic purposes, the field dimension is fixed to 100mx100m
    In order to facilitate the discovery of the virtual target, 
    it will be generated in the nearby locations of a flying drone 
    (first drone of the `swarm` instance).
    Specifically, this will be addressed specifying the radius of 
    the circumference where target must spawn. 
    """ 
    assert max_radius > 1, "Target can not be in the same location of the drone"
    
    # retrieve starting point and generate a spawn location
    drones_pos = await swarm.positions
    start_pos = drones_pos[0]

    alpha = 2 * math.pi * random.random()
    u = random.random() + random.random()
    r = max_radius * (2 - u if u > 1 else u)
    
    target_x_incr = r * math.cos(alpha)
    target_y_incr = r * math.sin(alpha)
    target_z_incr = 0

    # virtual target will be calculated shifting in the two dimensions (X, Y, Z = 0) from the takeoff point of the first drone of the swarm
    virtual_target = start_pos.increment_m(target_x_incr, target_y_incr, target_z_incr)
    return virtual_target

# -----------------

async def main():
    global VIRTUAL_TARGET
    
    swarm = Swarm(6)
    await swarm.connect()

    # first virtual target creation
    while VIRTUAL_TARGET == None:
        VIRTUAL_TARGET = await create_virtual_target(swarm, 40)
    logger.debug(f"Virtual Target: {VIRTUAL_TARGET}")

    # run simulation
    spawns = await swarm.positions
    stigmergy_simulation = Stigmergy(swarm, spawns[0])
    await stigmergy_simulation.start()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())