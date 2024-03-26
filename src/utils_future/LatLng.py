from dataclasses import dataclass


@dataclass
class LatLng:
    lat: float
    lng: float

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
