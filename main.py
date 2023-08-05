# --- DEPENDENCIES ---
from loguru import logger

import asyncio
import random
import math

from models.swarm import Swarm
from models.droneposition import DronePosition

from stigmergy import Stigmergy
# --------------------

# --- GLOBAL VARIABLES ---
VIRTUAL_TARGET = None   # virtual target generated on working field
# ------------------------

# --- FUNCTIONS ---

"""
Creates a random virtual target inside the specified working field.
For academic purposes, the field dimension is fixed to 1km x 1km
In order to facilitate the discovery of the virtual target, it will be generated in the nearby locations of a flying drone 
(first drone of the `swarm` instance).
Specifically, this will be addressed specifying the radius of the circumference where target must spawn. 
"""
async def create_virtual_target(swarm:Swarm, max_radius) -> DronePosition:
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

# Function passed to the Swarm to act as a Virtual Sensor to detect the target. 
# Just one multicopter will be able to virtually sense the target (the first one), in order to test the stigmergic algorithm. 
# The other components of the swarm will be heading randomly across the working field until they sense the pheromone.
async def target_scanner(drone) -> float:
    # get drone position
    p = await anext(drone.telemetry.position())
    drone_pos = DronePosition.from_mavsdk_position(p)
    
    # calculate distance between drone and VIRTUAL_TARGET
    distance = drone_pos.distance_2D_m(VIRTUAL_TARGET)

    # return a value which exponentially decreases proportionally to the distance
    discovery = math.exp(-distance/10)
    return discovery 

# -----------------

async def main():
    global VIRTUAL_TARGET
    
    swarm = Swarm(target_scanner, 2)
    await swarm.connect()

    # virtual target creation
    while VIRTUAL_TARGET == None:
        VIRTUAL_TARGET = await create_virtual_target(swarm, 100)
    logger.debug(f"Virtual Target: {VIRTUAL_TARGET}")

    # DEBUG MODE
    # in order to check the current position of the virtual target on QGC
    # the software creates a drone which reaches the desired spot.
    # Attention! This drone does not interfere with the flying swarm and it is present only for visualizing the virtual target.
    # target_swarm = Swarm(lambda x: 0, 1) 
    # await target_swarm.connect()
    # await target_swarm.takeoff()
    # await asyncio.sleep(5)
    # await target_swarm.set_positions([VIRTUAL_TARGET])
    # await asyncio.sleep(10)
    # await target_swarm.land()

    # run simulation
    spawn = await swarm.positions
    stigmergy_simulation = Stigmergy(spawn[0])

if __name__ == "__main__":
    asyncio.run(main())