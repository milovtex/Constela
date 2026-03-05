from dataclasses import dataclass, field


@dataclass(slots=True)
class BirthData:
    name: str
    birth_date: str
    birth_time: str
    city: str
    country: str | None = None
    timezone: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass(slots=True)
class PlanetPlacement:
    planet: str
    sign: str | None = None
    house: str | None = None


@dataclass(slots=True)
class ChartSummary:
    sun: PlanetPlacement | None = None
    moon: PlanetPlacement | None = None
    ascendant: str | None = None
    planets: list[PlanetPlacement] = field(default_factory=list)
    raw_payload: dict = field(default_factory=dict)
