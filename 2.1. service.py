# service.py

from models import Driver, Passenger, RideRequest, Ride, Vehicle
from utils import calculate_distance, save_data, load_data, NoDriverFoundError, InvalidRequestError, Location
from datetime import timedelta

# Constants
BASE_RATE = 0.50  # Fare per km
TIME_RATE = 0.20  # Fare per minute
BASE_FARE = 2.50  # Starting fare

class RideService:
    """The main class that manages all driver, passenger, and ride data, coordinating operations."""
    def __init__(self):
        self._drivers = []
        self._passengers = []
        self._requests = []
        self._rides = []
        self._load_initial_data() # Persistence simulation

    # --- Data Management ---
    def _load_initial_data(self):
        """Loads simulated data when the application starts."""
        data = load_data()
        
        # Recreating objects in a real application would be more complex.
        # For this example, we simply clear and re-add the lists:
        print("Data Loaded.")
        
    # --- CRUD Operations ---
    def add_driver(self, driver: Driver):
        self._drivers.append(driver)

    def add_passenger(self, passenger: Passenger):
        self._passengers.append(passenger)

    def get_driver_by_id(self, driver_id: str) -> Driver:
        for driver in self._drivers:
            if driver.id == driver_id:
                return driver
        return None

    # --- Algorithmic Requirements ---

    # [cite_start]Fare Estimation (Requirement: Fare Estimation) [cite: 492]
    def _estimate_fare(self, distance_km: float) -> float:
        """Calculates the ride fare using a simple formula."""
        # Estimated time (assumption: 30 km/h average speed)
        estimated_time_min = (distance_km / 30) * 60
        
        fare = BASE_FARE + (distance_km * BASE_RATE) + (estimated_time_min * TIME_RATE)
        return round(fare, 2)

    # [cite_start]Nearest Available Driver Search (Requirement: Search for nearest available driver) [cite: 489]
    def _find_nearest_driver(self, pickup_loc: Location) -> tuple[Driver, float] | None:
        """
        Finds the nearest available driver and returns the distance to that driver.
        """
        nearest_driver = None
        min_distance = float('inf')

        available_drivers = [d for d in self._drivers if d.is_available]

        if not available_drivers:
            raise NoDriverFoundError("No available drivers currently.")

        for driver in available_drivers:
            distance = calculate_distance(driver.current_location, pickup_loc)
            if distance < min_distance:
                min_distance = distance
                nearest_driver = driver

        return nearest_driver, min_distance

    # [cite_start]Request Handling (Requirement: Handle user ride requests) [cite: 487]
    def request_ride(self, passenger: Passenger, pickup_loc: Location, dropoff_loc: Location) -> RideRequest:
        """Creates and processes a new ride request."""
        if pickup_loc.latitude == dropoff_loc.latitude and pickup_loc.longitude == dropoff_loc.longitude:
            raise InvalidRequestError("Pickup and dropoff locations cannot be the same.")
            
        request = RideRequest(passenger, pickup_loc, dropoff_loc)
        self._requests.append(request)
        
        print(f"\n[REQUEST] New request created for: {request.passenger.name}")
        return request

    # Assignment (Ride Assignment)
    def assign_ride(self, request: RideRequest) -> Ride:
        """Assigns a suitable driver to the ride request and starts the ride."""
        # 1. Find the nearest available driver.
        nearest_driver, driver_distance = self._find_nearest_driver(request.pickup_loc)

        # 2. Calculate ride distance and fare.
        ride_distance = calculate_distance(request.pickup_loc, request.dropoff_loc)
        fare = self._estimate_fare(ride_distance)

        # 3. Start the ride.
        new_ride = Ride(request, nearest_driver, fare, ride_distance)
        self._rides.append(new_ride)

        # 4. Update driver status.
        nearest_driver.set_availability(False)
        request.set_status("Assigned")

        print(f"[ASSIGNMENT] Driver {nearest_driver.name} assigned. Estimated Fare: {fare:.2f} TL, Distance: {ride_distance:.2f} km")
        return new_ride

    # Ride Completion
    def complete_ride(self, ride: Ride, rating: float, actual_distance: float, final_fare: float):
        """Simulates the completion of a ride and updates all data."""
        ride.complete(actual_distance, final_fare, rating)
        print(f"[COMPLETE] Ride completed. Earnings: {final_fare:.2f} TL. New Driver Rating: {ride.driver._rating:.2f}")

    # --- Reporting / Sorting ---

    # [cite_start]Sort Completed Rides (Requirement: Sort completed rides) [cite: 493]
    def sort_completed_rides(self, sort_by: str = 'rating', reverse: bool = True):
        """Sorts completed rides by rating or distance."""
        completed_rides = [r for r in self._rides if r._status == "Completed"]

        if sort_by == 'rating':
            # Sort by driver rating (indirectly)
            sorted_rides = sorted(completed_rides, key=lambda r: r.driver._rating, reverse=reverse)
        elif sort_by == 'distance':
            # Sort by estimated distance
            sorted_rides = sorted(completed_rides, key=lambda r: r.estimated_distance, reverse=reverse)
        else:
            print("Invalid sorting criterion.")
            return []
            
        return sorted_rides

    # --- Basic Analytics ---
    def generate_simple_analytics(self):
        """Generates simple analytical reports."""
        completed_rides = [r for r in self._rides if r._status == "Completed"]
        total_trips = len(completed_rides)
        total_fare = sum(r.fare for r in completed_rides)
        
        avg_trip_time = timedelta()
        if total_trips > 0:
            total_time = sum((r._end_time - r._start_time for r in completed_rides), timedelta())
            avg_trip_time = total_time / total_trips

        print("\n--- Basic System Analytics ---")
        print(f"Total Completed Rides: {total_trips}")
        print(f"Total Earnings: {total_fare:.2f} TL")
        print(f"Average Ride Duration: {avg_trip_time}") # 
        
    def save_state(self):
        """Saves the current system state."""
        data = {
            'drivers': [d.to_dict() for d in self._drivers],
            'passengers': [p.to_dict() for p in self._passengers],
            'requests': [r.to_dict() for r in self._requests],
            'rides': [r.to_dict() for r in self._rides],
        }
        save_data(data)

        print("\n[PERSISTENCE] All data successfully saved.")
