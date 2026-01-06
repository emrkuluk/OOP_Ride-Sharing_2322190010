# models.py

import uuid
from datetime import datetime
from utils import Location

# -----------------------------------------------------------
# 1. Base Class: Person
# -----------------------------------------------------------
class Person:
    """Base class for Driver and Passenger."""
    def __init__(self, name: str, phone: str, current_location: Location):
        self._id = str(uuid.uuid4())
        self._name = name # Encapsulation
        self._phone = phone
        self._current_location = current_location

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def current_location(self):
        return self._current_location

    def update_location(self, new_location: Location):
        """Method to update the current location."""
        self._current_location = new_location
        print(f"{self.name}'s location updated: {new_location}")

# -----------------------------------------------------------
# 2. Driver
# -----------------------------------------------------------
class Driver(Person):
    """Represents a driver in the Ride-Sharing system."""
    def __init__(self, name: str, phone: str, current_location: Location, vehicle):
        super().__init__(name, phone, current_location)
       self._vehicle = vehicle # Composition: A Driver has a Vehicle.
        self._is_available = True
        self._rating = 5.0
        self._total_rides = 0
        self._earnings = 0.0

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def is_available(self):
        return self._is_available

    def set_availability(self, status: bool):
        """Updates the driver's availability status."""
        self._is_available = status

    def complete_ride(self, fare: float, new_rating: float):
        """Updates driver statistics upon ride completion."""
        self._total_rides += 1
        self._earnings += fare
        # Simple rating update
        self._rating = (self._rating * (self._total_rides - 1) + new_rating) / self._total_rides
        self.set_availability(True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self._phone,
            'location': {'lat': self.current_location.latitude, 'lon': self.current_location.longitude},
            'vehicle': self.vehicle.to_dict(),
            'is_available': self.is_available,
            'rating': self._rating,
            'total_rides': self._total_rides,
            'earnings': self._earnings
        }

# -----------------------------------------------------------
# 3. Passenger
# -----------------------------------------------------------
class Passenger(Person):
    """Represents a passenger in the Ride-Sharing system."""
    def __init__(self, name: str, phone: str, current_location: Location):
        super().__init__(name, phone, current_location)
        self._total_rides = 0

    def complete_ride(self):
        self._total_rides += 1

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self._phone,
            'location': {'lat': self.current_location.latitude, 'lon': self.current_location.longitude},
            'total_rides': self._total_rides
        }

# -----------------------------------------------------------
# 4. Vehicle
# -----------------------------------------------------------
class Vehicle:
    """Represents a vehicle belonging to a driver."""
    def __init__(self, make: str, model: str, license_plate: str):
        self._make = make
        self._model = model
        self._license_plate = license_plate
        self._mileage = 0

    def add_mileage(self, distance: float):
        self._mileage += distance

    def to_dict(self):
        return {
            'make': self._make,
            'model': self._model,
            'license_plate': self._license_plate,
            'mileage': self._mileage
        }

# -----------------------------------------------------------
# 5. RideRequest
# -----------------------------------------------------------
class RideRequest:
    """Represents a ride request created by a passenger."""
    def __init__(self, passenger: Passenger, pickup_loc: Location, dropoff_loc: Location):
        self._id = str(uuid.uuid4())
        self._passenger = passenger
        self._pickup_loc = pickup_loc
        self._dropoff_loc = dropoff_loc
        self._timestamp = datetime.now()
        self._status = "Pending"

    @property
    def id(self):
        return self._id

    @property
    def passenger(self):
        return self._passenger

    @property
    def pickup_loc(self):
        return self._pickup_loc

    @property
    def dropoff_loc(self):
        return self._dropoff_loc

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def status(self):
        return self._status

    def set_status(self, status: str):
        self._status = status

    def to_dict(self):
        return {
            'id': self.id,
            'passenger_id': self.passenger.id,
            'pickup': {'lat': self.pickup_loc.latitude, 'lon': self.pickup_loc.longitude},
            'dropoff': {'lat': self.dropoff_loc.latitude, 'lon': self.dropoff_loc.longitude},
            'timestamp': str(self.timestamp),
            'status': self.status
        }
        
# -----------------------------------------------------------
# 6. Ride
# -----------------------------------------------------------
class Ride:
    """Represents a confirmed and ongoing ride."""
    def __init__(self, request: RideRequest, driver: Driver, fare: float, estimated_distance: float):
        self._id = str(uuid.uuid4())
        self._request = request
        self._driver = driver
        self._start_time = datetime.now()
        self._end_time = None
        self._fare = fare
        self._estimated_distance = estimated_distance
        self._status = "In Progress"

    @property
    def driver(self):
        return self._driver

    @property
    def estimated_distance(self):
        return self._estimated_distance

    @property
    def fare(self):
        return self._fare

    def complete(self, actual_distance: float, final_fare: float, rating: float):
        """Finalizes the ride and updates related objects."""
        self._end_time = datetime.now()
        self._status = "Completed"
        self._driver.update_location(self._request.dropoff_loc)
        self._driver.complete_ride(final_fare, rating)
        self._driver.vehicle.add_mileage(actual_distance)
        self._request.passenger.complete_ride()
        
    def to_dict(self):
        return {
            'id': self._id,
            'request_id': self._request.id,
            'driver_id': self._driver.id,
            'start_time': str(self._start_time),
            'end_time': str(self._end_time),
            'estimated_distance': self._estimated_distance,
            'fare': self._fare,
            'status': self._status
        }

