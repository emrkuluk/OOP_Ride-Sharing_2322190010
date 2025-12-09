# service.py

from models import Driver, Passenger, RideRequest, Ride, Vehicle
from utils import calculate_distance, save_data, load_data, NoDriverFoundError, InvalidRequestError, Location
from datetime import timedelta

# Sabitler
BASE_RATE = 0.50  # km başına ücret
TIME_RATE = 0.20  # dakika başına ücret
BASE_FARE = 2.50  # Başlangıç ücreti

class RideService:
    """Tüm sürücü, yolcu ve sürüş verilerini yöneten ve işlemleri koordine eden ana sınıf."""
    def __init__(self):
        self._drivers = []
        self._passengers = []
        self._requests = []
        self._rides = []
        self._load_initial_data() # Kalıcılık simülasyonu

    # --- Veri Yönetimi ---
    def _load_initial_data(self):
        """Uygulama başladığında simüle edilmiş verileri yükler."""
        data = load_data()
        
        # Gerçek uygulamada nesneleri yeniden oluşturmak daha karmaşık olacaktır.
        # Bu örnekte, basitçe listeleri temizleyip yeniden ekleyelim:
        print("Veriler Yüklendi.")
        
    # --- CRUD İşlemleri ---
    def add_driver(self, driver: Driver):
        self._drivers.append(driver)

    def add_passenger(self, passenger: Passenger):
        self._passengers.append(passenger)

    def get_driver_by_id(self, driver_id: str) -> Driver:
        for driver in self._drivers:
            if driver.id == driver_id:
                return driver
        return None

    # --- Algoritmik Gereklilikler ---

    # Fare Estimation (Ücret Tahmini) [cite: 492]
    def _estimate_fare(self, distance_km: float) -> float:
        """Basit bir formül kullanarak sürüş ücretini hesaplar."""
        # Tahmini süre (varsayım: 30 km/saat ortalama hız)
        estimated_time_min = (distance_km / 30) * 60
        
        fare = BASE_FARE + (distance_km * BASE_RATE) + (estimated_time_min * TIME_RATE)
        return round(fare, 2)

    # Nearest Available Driver Search (En Yakın Sürücü Arama) [cite: 489]
    def _find_nearest_driver(self, pickup_loc: Location) -> tuple[Driver, float] | None:
        """
        En yakın müsait sürücüyü bulur ve o sürücüye olan mesafeyi döndürür.
        """
        nearest_driver = None
        min_distance = float('inf')

        available_drivers = [d for d in self._drivers if d.is_available]

        if not available_drivers:
            raise NoDriverFoundError("Şu anda müsait sürücü yok.")

        for driver in available_drivers:
            distance = calculate_distance(driver.current_location, pickup_loc)
            if distance < min_distance:
                min_distance = distance
                nearest_driver = driver

        return nearest_driver, min_distance

    # Request Handling (Talep İşleme) [cite: 487]
    def request_ride(self, passenger: Passenger, pickup_loc: Location, dropoff_loc: Location) -> RideRequest:
        """Yeni bir sürüş talebi oluşturur ve işler."""
        if pickup_loc.latitude == dropoff_loc.latitude and pickup_loc.longitude == dropoff_loc.longitude:
            raise InvalidRequestError("Alış ve bırakış konumları aynı olamaz.")
            
        request = RideRequest(passenger, pickup_loc, dropoff_loc)
        self._requests.append(request)
        
        print(f"\n[REQUEST] Yeni talep oluşturuldu: {request.passenger.name}")
        return request

    # Assignment (Sürüş Atama)
    def assign_ride(self, request: RideRequest) -> Ride:
        """Sürüş talebine uygun sürücü atar ve sürüşü başlatır."""
        # 1. En yakın müsait sürücüyü bul.
        nearest_driver, driver_distance = self._find_nearest_driver(request.pickup_loc)

        # 2. Sürüş mesafesini ve ücreti hesapla.
        ride_distance = calculate_distance(request.pickup_loc, request.dropoff_loc)
        fare = self._estimate_fare(ride_distance)

        # 3. Sürüşü başlat.
        new_ride = Ride(request, nearest_driver, fare, ride_distance)
        self._rides.append(new_ride)

        # 4. Sürücü durumunu güncelle.
        nearest_driver.set_availability(False)
        request.set_status("Assigned")

        print(f"[ASSIGNMENT] Sürücü {nearest_driver.name} atandı. Tahmini Ücret: {fare:.2f} TL, Mesafe: {ride_distance:.2f} km")
        return new_ride

    # Ride Completion (Sürüş Tamamlama)
    def complete_ride(self, ride: Ride, rating: float, actual_distance: float, final_fare: float):
        """Bir sürüşün tamamlanmasını simüle eder ve tüm verileri günceller."""
        ride.complete(actual_distance, final_fare, rating)
        print(f"[COMPLETE] Sürüş tamamlandı. Kazanç: {final_fare:.2f} TL. Yeni Sürücü Puanı: {ride.driver._rating:.2f}")

    # --- Raporlama / Sıralama ---

    # Sort Completed Rides (Tamamlanmış Sürüşleri Sıralama) [cite: 493]
    def sort_completed_rides(self, sort_by: str = 'rating', reverse: bool = True):
        """Tamamlanmış sürüşleri puana veya mesafeye göre sıralar."""
        completed_rides = [r for r in self._rides if r._status == "Completed"]

        if sort_by == 'rating':
            # Sürücünün puanına göre sıralama (dolaylı)
            sorted_rides = sorted(completed_rides, key=lambda r: r.driver._rating, reverse=reverse)
        elif sort_by == 'distance':
            # Tahmini mesafeye göre sıralama
            sorted_rides = sorted(completed_rides, key=lambda r: r.estimated_distance, reverse=reverse)
        else:
            print("Geçersiz sıralama kriteri.")
            return []
            
        return sorted_rides

    # --- Basit Analitik ---
    def generate_simple_analytics(self):
        """Basit analitik raporlar oluşturur."""
        completed_rides = [r for r in self._rides if r._status == "Completed"]
        total_trips = len(completed_rides)
        total_fare = sum(r.fare for r in completed_rides)
        
        avg_trip_time = timedelta()
        if total_trips > 0:
            total_time = sum((r._end_time - r._start_time for r in completed_rides), timedelta())
            avg_trip_time = total_time / total_trips

        print("\n--- Basic System Analytics ---")
        print(f"Toplam Tamamlanan Sürüş: {total_trips}")
        print(f"Toplam Kazanılan Ücret: {total_fare:.2f} TL")
        print(f"Ortalama Sürüş Süresi: {avg_trip_time}") # 
        
    def save_state(self):
        """Mevcut sistem durumunu kaydeder."""
        data = {
            'drivers': [d.to_dict() for d in self._drivers],
            'passengers': [p.to_dict() for p in self._passengers],
            'requests': [r.to_dict() for r in self._requests],
            'rides': [r.to_dict() for r in self._rides],
        }
        save_data(data)
        print("\n[PERSISTENCE] Tüm veriler başarıyla kaydedildi.")