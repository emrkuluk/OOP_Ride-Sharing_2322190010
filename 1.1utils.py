# utils.py

import json
from math import radians, sin, cos, sqrt, atan2

# Geographical Calculation Constants
EARTH_RADIUS_KM = 6371

# -----------------------------------------------------------
# 1. Location (Value Object - Immutability)
# Simple coordinate class for Driver/Passenger locations
# -----------------------------------------------------------
class Location:
    """Immutable value object representing geographical coordinates."""
    def __init__(self, lat: float, lon: float):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Invalid latitude/longitude values.")
        # Encapsulation and Immutability: Attributes cannot be directly modified.
        self._latitude = lat
        self._longitude = lon

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    def __repr__(self):
        return f"Location(lat={self.latitude:.4f}, lon={self.longitude:.4f})"

# -----------------------------------------------------------
# 2. Distance Calculation (Haversine Formula)
# -----------------------------------------------------------
def calculate_distance(loc1: Location, loc2: Location) -> float:
    """Calculates the distance (km) between two Location objects using the Haversine formula."""
    lat1, lon1 = radians(loc1.latitude), radians(loc1.longitude)
    lat2, lon2 = radians(loc2.latitude), radians(loc2.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = EARTH_RADIUS_KM * c
    return distance

# -----------------------------------------------------------
# 3. Data Persistence Simulation
# -----------------------------------------------------------
def save_data(data, filename="rideshare_data.json"):
    """Saves data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, default=str)

def load_data(filename="rideshare_data.json"):
    """Loads data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'drivers': [], 'passengers': [], 'requests': [], 'rides': []}

# -----------------------------------------------------------
# 4. Custom Exceptions (Requirement)
# -----------------------------------------------------------
class ServiceError(Exception):
    """Base exception class for general RideService errors."""
    pass

class NoDriverFoundError(ServiceError):
    """Triggered when no suitable driver is found."""
    pass
    
class InvalidRequestError(ServiceError):
    """Triggered when a ride request is invalid."""
    pass
