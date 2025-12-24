# service.py (Eklenen Metotlar)

    # Optimal Assignment Algorithm (Sürücü-Yolcu Eşleştirme) 
    def _optimized_driver_matching(self, request: RideRequest) -> tuple[Driver, float] | None:
        """
        Greedy algoritma kullanarak optimal sürücü-yolcu eşleştirmesini uygular.
        Hedef: Sürücünün yolcuya ulaşma süresini (dolayısıyla yolcunun bekleme süresini) minimize etmek.
        """
        available_drivers = [d for d in self._drivers if d.is_available]
        
        if not available_drivers:
            raise NoDriverFoundError("Şu anda müsait sürücü yok.")

        best_driver = None
        min_arrival_time = float('inf') # Sürücünün yolcuya ulaşma süresini minimize et

        # Ortalama hız varsayımı (km/dakika)
        AVG_SPEED_KM_PER_MIN = 0.5 

        for driver in available_drivers:
            # 1. Sürücünün yolcuya olan mesafesi (driver-to-pickup)
            driver_to_pickup_dist = calculate_distance(driver.current_location, request.pickup_loc)
            
            # 2. Yolcuya tahmini varış süresi (bekleme süresi)
            estimated_arrival_time_min = driver_to_pickup_dist / AVG_SPEED_KM_PER_MIN
            
            # Basit Greedy Kuralı: En kısa varış süresi (min bekleme süresi) 
            if estimated_arrival_time_min < min_arrival_time:
                min_arrival_time = estimated_arrival_time_min
                best_driver = driver
                
        # Atanan sürücü ve sürücü-yolcu mesafesi
        driver_to_pickup_dist = calculate_distance(best_driver.current_location, request.pickup_loc)
        return best_driver, driver_to_pickup_dist

    # assign_ride metodunu bu yeni optimizasyon algoritmasını kullanacak şekilde güncelleyin:
    def assign_ride(self, request: RideRequest) -> Ride:
        """Sürüş talebine uygun optimal sürücü atar ve sürüşü başlatır."""
        try:
            # Stage 3: Optimize edilmiş eşleştirmeyi kullan 
            nearest_driver, driver_distance = self._optimized_driver_matching(request)
        except NoDriverFoundError as e:
            print(f"Hata: {e}")
            raise e

        # 2. Sürüş mesafesini ve ücreti hesapla.
        ride_distance = calculate_distance(request.pickup_loc, request.dropoff_loc)
        fare = self._estimate_fare(ride_distance)

        # 3. Sürüşü başlat.
        new_ride = Ride(request, nearest_driver, fare, ride_distance)
        self._rides.append(new_ride)

        # 4. Sürücü durumunu güncelle.
        nearest_driver.set_availability(False)
        request.set_status("Assigned")

        print(f"[ASSIGNMENT] Optimal Sürücü {nearest_driver.name} atandı. Bekleme süresi ~{driver_distance/0.5:.1f} dakika.")
        return new_ride

    # Advanced Analytics (Gelişmiş Analitik) 
    def generate_advanced_analytics(self):
        """Ortalama gezi süresi ve memnuniyet endeksi gibi gelişmiş raporlar oluşturur."""
        completed_rides = [r for r in self._rides if r._status == "Completed"]
        total_trips = len(completed_rides)
        
        avg_rating = sum(r.driver._rating for r in self._drivers) / len(self._drivers) if self._drivers else 0
        
        # Ortalama Seyahat Süresi
        avg_trip_time = timedelta()
        if total_trips > 0:
            total_time = sum((r._end_time - r._start_time for r in completed_rides), timedelta())
            avg_trip_time = total_time / total_trips

        print("\n--- Advanced Analytics ---")
        print(f"Toplam Tamamlanan Sürüş: {total_trips}")
        print(f"Sürücü Memnuniyet Endeksi (Ort. Puan): {avg_rating:.2f} / 5.0")
        print(f"Ortalama Trip Süresi: {str(avg_trip_time).split('.')[0]}")