# utils.py

import json
from math import radians, sin, cos, sqrt, atan2

# Coğrafi Hesaplama Sabitleri
EARTH_RADIUS_KM = 6371

# -----------------------------------------------------------
# 1. Money (Value Object - Immutability)
# Sürücü/Yolcu konumları için basit koordinat sınıfı
# -----------------------------------------------------------
class Location:
    """Konum koordinatlarını temsil eden değişmez (immutable) değer nesnesi."""
    def __init__(self, lat: float, lon: float):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Geçersiz enlem/boylam değerleri.")
        # Kapsülleme ve Değişmezlik: Özellikler doğrudan değiştirilemez.
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
# 2. Distance Calculation (Haversine Formülü)
# -----------------------------------------------------------
def calculate_distance(loc1: Location, loc2: Location) -> float:
    """İki Location nesnesi arasındaki mesafeyi (km) Haversine formülü ile hesaplar."""
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
    """Veriyi JSON dosyasına kaydeder."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, default=str)

def load_data(filename="rideshare_data.json"):
    """Veriyi JSON dosyasından yükler."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'drivers': [], 'passengers': [], 'requests': [], 'rides': []}

# -----------------------------------------------------------
# 4. Custom Exceptions (Gereklilik)
# -----------------------------------------------------------
class ServiceError(Exception):
    """Genel RideService hataları için temel istisna sınıfı."""
    pass

class NoDriverFoundError(ServiceError):
    """Uygun sürücü bulunamadığında tetiklenir."""
    pass
    
class InvalidRequestError(ServiceError):
    """Geçersiz bir sürüş talebi olduğunda tetiklenir."""
    pass