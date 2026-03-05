from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import inspect
from typing import Any

from constela.models import BirthData, ChartSummary, PlanetPlacement


class AstrologyError(RuntimeError):
    pass


def _coalesce(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _extract_planet(subject: Any, planet_name: str) -> PlanetPlacement | None:
    entry = getattr(subject, planet_name.lower(), None)
    if entry is None:
        return None

    sign = _coalesce(getattr(entry, "sign", None))
    house = _coalesce(getattr(entry, "house", None))
    return PlanetPlacement(planet=planet_name, sign=sign, house=house)


def _subject_payload(subject: Any) -> dict:
    if hasattr(subject, "model_dump") and callable(subject.model_dump):
        dumped = subject.model_dump()
        if isinstance(dumped, dict):
            return dumped
    if hasattr(subject, "__dict__") and isinstance(subject.__dict__, dict):
        return dict(subject.__dict__)
    return {}


def calculate_natal_chart(data: BirthData) -> ChartSummary:
    try:
        from kerykeion import AstrologicalSubject
    except ModuleNotFoundError as exc:
        raise AstrologyError(
            "Falta dependencia 'kerykeion'. Instala con: pip install kerykeion"
        ) from exc

    try:
        birth_dt = datetime.strptime(f"{data.birth_date} {data.birth_time}", "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise AstrologyError("Fecha/hora invalida. Usa YYYY-MM-DD y HH:MM.") from exc

    sig = inspect.signature(AstrologicalSubject)
    kwargs: dict[str, Any] = {}
    candidate = {
        "name": data.name,
        "year": birth_dt.year,
        "month": birth_dt.month,
        "day": birth_dt.day,
        "hour": birth_dt.hour,
        "minute": birth_dt.minute,
        "city": data.city,
        "nation": data.country,
        "country": data.country,
        "tz_str": data.timezone,
        "timezone": data.timezone,
        "lat": data.latitude,
        "lng": data.longitude,
        "lon": data.longitude,
    }
    for param in sig.parameters:
        if param in candidate and candidate[param] is not None:
            kwargs[param] = candidate[param]

    try:
        subject = AstrologicalSubject(**kwargs)
    except Exception as exc:  # pragma: no cover - runtime integration boundary
        raise AstrologyError(f"No se pudo calcular la carta natal: {exc}") from exc

    planets: list[PlanetPlacement] = []
    for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        placement = _extract_planet(subject, name)
        if placement is not None:
            planets.append(placement)

    payload = _subject_payload(subject)
    if not planets and isinstance(payload.get("planets"), list):
        for planet_data in payload["planets"]:
            if not isinstance(planet_data, dict):
                continue
            planets.append(
                PlanetPlacement(
                    planet=_coalesce(planet_data.get("name")) or "Unknown",
                    sign=_coalesce(planet_data.get("sign")),
                    house=_coalesce(planet_data.get("house")),
                )
            )

    sun = next((p for p in planets if p.planet.lower() == "sun"), None)
    moon = next((p for p in planets if p.planet.lower() == "moon"), None)

    ascendant = _coalesce(getattr(subject, "ascendant_sign", None))
    if not ascendant and isinstance(payload.get("first_house"), dict):
        ascendant = _coalesce(payload["first_house"].get("sign"))

    chart = ChartSummary(
        sun=sun,
        moon=moon,
        ascendant=ascendant,
        planets=planets,
        raw_payload=payload,
    )
    chart.raw_payload.setdefault("input", asdict(data))
    return chart
