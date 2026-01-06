from models import Driver, Passenger, Vehicle
from service import RideService, NoDriverFoundError, InvalidRequestError
from utils import Location

def setup_simulation(service: RideService):
    d1_vehicle = Vehicle("Toyota", "Corolla", "34 ABC 123")
    d1 = Driver("Ahmet Yilmaz", "555-1000", Location(41.0082, 28.9784), d1_vehicle)
    
    d2_vehicle = Vehicle("Renault", "Clio", "34 DEF 456")
    d2 = Driver("Buse Kaya", "555-2000", Location(41.0401, 29.0069), d2_vehicle)
    
    service.add_driver(d1)
    service.add_driver(d2)

    p1 = Passenger("Emirhan Kuluk", "555-4000", Location(41.0345, 29.0000)) 
    p2 = Passenger("Ayse Celik", "555-5000", Location(41.0100, 28.9700)) 
    
    service.add_passenger(p1)
    service.add_passenger(p2)
    
    print("--- Stage 1: Architecture Setup Complete ---")

def run_simulation(service: RideService):
    print("\n" + "="*50)
    print("RIDE-SHARING SYSTEM STAGE 3 SIMULATION")
    print("="*50)

    passenger = service._passengers[0]
    pickup = passenger.current_location
    dropoff = Location(40.9850, 29.0596)

    try:
        request = service.request_ride(passenger, pickup, dropoff)
        ride = service.assign_ride(request)
        
        print("\n--- Processing Ride Completion ---")
        service.complete_ride(ride, rating=4.9, actual_distance=11.2, final_fare=18.50)
        
    except (NoDriverFoundError, InvalidRequestError) as e:
        print(f"Ride Execution Error: {e}")

    service.generate_simple_analytics()

    sorted_rides = service.sort_completed_rides(sort_by='rating')
    print("\n--- Completed Rides Sorted by Rating ---")
    for r in sorted_rides:
        print(f"Driver: {r.driver.name}, Rating: {r.driver._rating:.2f}")

    service.save_state()

if __name__ == "__main__":
    ride_sharing_app = RideService()
    setup_simulation(ride_sharing_app)
    run_simulation(ride_sharing_app)

