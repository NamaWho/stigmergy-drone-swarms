import random

from models.swarm import Swarm
from models.droneposition import DronePosition, m_to_deg

def get_virtual_target(lower_bound_x, lower_bound_y, side_length) -> DronePosition:
    """
    Creates a new random virtual target inside the specified working field.
    In order to facilitate the discovery of the virtual target, it will be generated in the nearby locations of a flying drone 
    (first drone of the `swarm` instance).
    Specifically, this will be addressed specifying the radius of the circumference where target must spawn. 
    """
    virtual_target = DronePosition(0,0,0)

    # Update the position based on random velocity
    new_latitude = lower_bound_x + random.randint(0, side_length-1)
    new_longitude = lower_bound_y + random.randint(0, side_length-1)

    virtual_target.latitude_deg = m_to_deg(new_latitude)
    virtual_target.longitude_deg = m_to_deg(new_longitude)
    virtual_target.absolute_altitude_m = 490

    return virtual_target
