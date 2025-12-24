from models import Driver, Passenger, RideRequest, Ride, Vehicle
from utils import calculate_distance, save_data, load_data, NoDriverFoundError, InvalidRequestError, Location
from datetime import timedelta

BASE_RATE = 0.50  
TIME_RATE = 0.20  
BASE_FARE = 2.50  

class RideService:
    def __init__(self):
        self._drivers = []
        self._passengers = []
        self._requests = []
        self._rides = []
        self._load_initial_data()

    def _load_initial_data(self):
        data = load_data()
        print("Initial Data Loaded.")
        
    def add_driver(self, driver: Driver):
        self._drivers.append(driver)

    def add_passenger(self, passenger: Passenger):
        self._passengers.append(passenger)

    def _estimate_fare(self, distance_km: float) -> float:
        estimated_time_min = (distance_km / 30) * 60
        fare = BASE_FARE + (distance_km * BASE_RATE) + (estimated_time_min * TIME_RATE)
        return round(fare, 2)

    def _optimized_driver_matching(self, request: RideRequest) -> tuple[Driver, float] | None:
        available_drivers = [d for d in self._drivers if d.is_available]
        if not available_drivers:
            raise NoDriverFoundError("No available drivers found.")

        best_driver = None
        min_arrival_time = float('inf')
        AVG_SPEED_KM_PER_MIN = 0.5 

        for driver in available_drivers:
            dist = calculate_distance(driver.current_location, request.pickup_loc)
            arrival_time = dist / AVG_SPEED_KM_PER_MIN
            if arrival_time < min_arrival_time:
                min_arrival_time = arrival_time
                best_driver = driver
                
        return best_driver, calculate_distance(best_driver.current_location, request.pickup_loc)

    def request_ride(self, passenger: Passenger, pickup_loc: Location, dropoff_loc: Location) -> RideRequest:
        if pickup_loc.latitude == dropoff_loc.latitude and pickup_loc.longitude == dropoff_loc.longitude:
            raise InvalidRequestError("Pickup and dropoff locations cannot be identical.")
        request = RideRequest(passenger, pickup_loc, dropoff_loc)
        self._requests.append(request)
        return request

    def assign_ride(self, request: RideRequest) -> Ride:
        matched_driver, dist = self._optimized_driver_matching(request)
        ride_dist = calculate_distance(request.pickup_loc, request.dropoff_loc)
        fare = self._estimate_fare(ride_dist)
        new_ride = Ride(request, matched_driver, fare, ride_dist)
        self._rides.append(new_ride)
        matched_driver.set_availability(False)
        request.set_status("Assigned")
        return new_ride

    def complete_ride(self, ride: Ride, rating: float, actual_distance: float, final_fare: float):
        ride.complete(actual_distance, final_fare, rating)

    def sort_completed_rides(self, sort_by='rating'):
        completed = [r for r in self._rides if r._status == "Completed"]
        if sort_by == 'rating':
            return sorted(completed, key=lambda r: r.driver._rating, reverse=True)
        return sorted(completed, key=lambda r: r.estimated_distance, reverse=True)

    def generate_advanced_analytics(self):
        completed = [r for r in self._rides if r._status == "Completed"]
        total_trips = len(completed)
        avg_rating = sum(d._rating for d in self._drivers) / len(self._drivers) if self._drivers else 0
        
        avg_time = timedelta()
        if total_trips > 0:
            total_time = sum((r._end_time - r._start_time for r in completed), timedelta())
            avg_time = total_time / total_trips

        print("\n--- Advanced Analytics ---")
        print(f"Total Completed Trips: {total_trips}")
        print(f"Satisfaction Index (Avg Rating): {avg_rating:.2f}")
        print(f"Average Trip Duration: {str(avg_time).split('.')[0]}")
        
    def save_state(self):
        data = {
            'drivers': [d.to_dict() for d in self._drivers],
            'passengers': [p.to_dict() for p in self._passengers],
            'rides': [r.to_dict() for r in self._rides]
        }
        save_data(data)
