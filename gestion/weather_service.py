# CODE pour gestion/weather_service.py

import random
import hashlib
from datetime import datetime

class MockWeatherService:
    def get_weather(self, city_name: str, dt: datetime) -> dict:
        seed_str = f"{city_name}-{dt.year}-{dt.month}-{dt.day}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        rng = random.Random(seed)
        is_rainy_day = rng.random() < 0.20
        if not is_rainy_day:
            return {'condition': 'clair', 'description': 'Ciel dégagé'}
        start_rain_hour = rng.randint(6, 18)
        if start_rain_hour <= dt.hour < start_rain_hour + 4:
            return {'condition': 'pluie', 'description': 'Pluie modérée'}
        else:
            return {'condition': 'clair', 'description': 'Nuageux'}