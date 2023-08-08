from math import floor

def calculate_square_boundaries(drone_position_x, drone_position_y, side_length):
    half_side = side_length / 2.0

    drone_position_x = floor(drone_position_x)
    drone_position_y = floor(drone_position_y)

    upper_left = (drone_position_x - half_side, drone_position_y + half_side)
    upper_right = (drone_position_x + half_side, drone_position_y + half_side)
    lower_left = (drone_position_x - half_side, drone_position_y - half_side)
    lower_right = (drone_position_x + half_side, drone_position_y - half_side)

    return [upper_left, upper_right, lower_left, lower_right]

def is_inside_square(x, y, boundaries):
    upper_left, upper_right, lower_left, lower_right = boundaries

    # Check if the coordinates are within the x and y boundaries
    if upper_left[0] <= x <= upper_right[0] and lower_left[0] <= x <= lower_right[0]:
        if lower_left[1] <= y <= upper_left[1] and lower_right[1] <= y <= upper_right[1]:
            return True

    return False