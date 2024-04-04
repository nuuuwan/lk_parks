from dataclasses import dataclass
from functools import cache, cached_property


@dataclass
class LatLng:
    lat: float
    lng: float

    def __str__(self) -> str:
        lat, lng = self.normalize.tuple
        return f'{lat:.6f},{lng:.6f}'

    def to_dict(self) -> dict:
        return {
            'lat': self.lat,
            'lng': self.lng,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            lat=d['lat'],
            lng=d['lng'],
        )

    @cached_property
    def normalize(self):
        lat, lng = self.tuple

        def norm(x):
            Q = 0.1**5
            return round(x / Q) * Q

        return LatLng(norm(lat), norm(lng))

    @cached_property
    def tuple(self) -> tuple[float, float]:
        return self.lat, self.lng

    @staticmethod
    def haversine(latlng1, latlng2):
        import math

        lat1, lon1 = latlng1
        lat2, lon2 = latlng2
        RADIUS = 6371
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
            math.radians(lat1)
        ) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) * math.sin(
            dlng / 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return RADIUS * c

    @cache
    def distance(self, other):
        return LatLng.haversine(self.tuple, other.tuple)
