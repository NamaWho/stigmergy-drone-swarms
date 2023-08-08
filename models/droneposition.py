import math
from typing import List
from mavsdk import telemetry
from geopy import distance as geo_distance

def deg_to_m(deg) -> float:
    # 1 deg = 111319.9 m
    return deg * 111319.9

def m_to_deg(m) -> float:
    return m / 111319.9

class DronePosition:
    """
    Stores a standard Position representation regardless the one used by MavSDK

    Implements methods to convert position in various formats (mavsdk.telemetry.position -> [float], DronePosition -> parameters list for action.goto_location ([float])...)
    Implements method to modify a `DronePosition` giving 3D axis displacements
    """
    def __init__(self,
                 latitude_deg:float,
                 longitude_deg:float,
                 absolute_altitude_m:float) -> None:
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg
        self.absolute_altitude_m = absolute_altitude_m
    
    @classmethod
    def from_mavsdk_position(cls, pos:telemetry.Position) -> None:
        """
        Defines the instance retrieving info by a Position object of MavSDK.

        Args:
            pos (telemetry.Position): Position object from which define the class instance
        """
        return cls(pos.latitude_deg, pos.longitude_deg, pos.absolute_altitude_m)

    # def __str__(self):
    #     return '%s(%s)' % (
    #         type(self).__name__,
    #         ', '.join('%s=%s' % item for item in vars(self).items())
    #     )
    
    def to_goto_location(self, prev_pos:'DronePosition'=None) -> List[float]:
        """
        Convert DronePosition to the correct format for action.goto_location.
        Desired format: goto_location(latitude_deg, longitude_deg, absolute_altitude_m, yaw_deg)
        
        Args:
            prev_pos (DronePosition, optional): Starting position.
                Used to calculate the `yaw` angle.
                If not specified, defaults to None.

        Returns:
            List[float]: Coordinates float list with the following format:
                (lat_deg, long_deg, abs_alt_m, yaw)
        """
        if prev_pos == None:
            yaw = 0
        else:
            d_lat = self.latitude_deg - prev_pos.latitude_deg
            d_lon = self.longitude_deg - prev_pos.longitude_deg
            # tan_angle = 90 + d_lon/d_lat
            # yaw = math.atan(tan_angle)
            yaw_rad = math.atan2(d_lat, d_lon)
            yaw = math.degrees(yaw_rad)
            yaw = (yaw + 360) % 360 - 90
        return (self.latitude_deg, self.longitude_deg, self.absolute_altitude_m, yaw)
    
    def increment_m(self, lat_increment_m, long_increment_m, alt_increment_m) -> 'DronePosition':
        """
        Modifies the current position with 3D displacements passed as arguments

        Args:
            lat_increment_m (_type_): latitude displacement [m]
            long_increment_m (_type_): longitude displacement [m] 
            alt_increment_m (_type_): altitude displacement [m] 

        Returns:
            DronePosition: New current DronePosition
        """
        new_lat = self.latitude_deg + m_to_deg(lat_increment_m)
        new_lon = self.longitude_deg + m_to_deg(long_increment_m)
        new_alt = self.absolute_altitude_m + alt_increment_m
        return DronePosition(new_lat, new_lon, new_alt)

    def distance_2D_m(self, point:'DronePosition') -> float:
        """
        Calculates 2D distance between two DronePosition

        Args:
            point (DronePosition): point desired

        Returns:
            float: Distance from `point`
        """
        # point1 = (self.latitude_deg, self.longitude_deg)
        # point2 = (point.latitude_deg, point.longitude_deg)

        # distance = geo_distance.distance(point1, point2).meters
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(self.latitude_deg)
        lon1_rad = math.radians(self.longitude_deg)
        lat2_rad = math.radians(point.latitude_deg)
        lon2_rad = math.radians(point.longitude_deg)

        # Haversine formula
        d_lat = lat2_rad - lat1_rad
        d_lon = lon2_rad - lon1_rad
        a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lon/2) * math.sin(d_lon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        radius_earth = 6371000  # Earth's radius in meters
        distance = radius_earth * c

        return distance
        # return distance