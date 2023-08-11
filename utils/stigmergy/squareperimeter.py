from math import floor

def calculate_square_boundaries(drone_position_x, drone_position_y, side_length):
    """
    Given a physical position (x, y)[m] and the length of the square perimeter 
    where simulation has to be ran, returns the four extremes of the perimeter (x, y)[m]
    """
    half_side = side_length / 2.0

    drone_position_x = floor(drone_position_x)
    drone_position_y = floor(drone_position_y)

    upper_left = (drone_position_x - half_side, drone_position_y + half_side)
    upper_right = (drone_position_x + half_side, drone_position_y + half_side)
    lower_left = (drone_position_x - half_side, drone_position_y - half_side)
    lower_right = (drone_position_x + half_side, drone_position_y - half_side)

    return [upper_left, upper_right, lower_left, lower_right]
