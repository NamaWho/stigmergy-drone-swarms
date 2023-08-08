import math

from models.droneposition import DronePosition, deg_to_m

def get_patch_coords(lower_bound_x,
                     lower_bound_y,
                     side_length,
                     total_patches:int,
                     position:DronePosition) -> (int, int):
    """
    Function used to retrieve patch coordinates of the current position of a drone
    
    Returns: patch coordinates of the working field
    """
    pos_x = position.latitude_deg
    pos_y = position.longitude_deg

    pos_x_m = deg_to_m(pos_x)
    pos_y_m = deg_to_m(pos_y)

    patch_length = math.ceil(side_length/total_patches)

    x_index = math.floor((pos_x_m - lower_bound_x) / patch_length)
    y_index = math.floor((pos_y_m - lower_bound_y) / patch_length)

    # logger.debug(f"LAT: {pos_x_m}, LONG: {pos_y_m}, X: {x_index}, Y: {y_index}")

    return (x_index, y_index)

    