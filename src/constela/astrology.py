from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import inspect
import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen
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


def _resolve_city_location(city: str, country: str | None = None) -> dict[str, Any] | None:
    query = city.strip()
    if country:
        query = f"{query}, {country.strip()}"

    params = {
        "name": query,
        "count": "1",
        "language": "es",
        "format": "json",
    }
    url = f"https://geocoding-api.open-meteo.com/v1/search?{urlencode(params)}"

    try:
        with urlopen(url, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    results = payload.get("results")
    if not isinstance(results, list) or not results:
        return None

    first = results[0]
    lat = first.get("latitude")
    lng = first.get("longitude")
    tz_str = first.get("timezone")
    if lat is None or lng is None or not tz_str:
        return None

    return {
        "city": first.get("name") or city,
        "country_code": first.get("country_code"),
        "lat": float(lat),
        "lng": float(lng),
        "tz_str": str(tz_str),
    }


def resolve_city_preview(city: str, country: str | None = None) -> dict[str, Any] | None:
    return _resolve_city_location(city=city, country=country)


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

    resolved_location: dict[str, Any] | None = None
    needs_resolution = (
        data.latitude is None
        or data.longitude is None
        or not data.timezone
        or not data.country
    )
    if needs_resolution:
        resolved_location = _resolve_city_location(data.city, data.country)

    latitude = data.latitude
    longitude = data.longitude
    timezone = data.timezone
    country = data.country

    if resolved_location is not None:
        if latitude is None:
            latitude = resolved_location["lat"]
        if longitude is None:
            longitude = resolved_location["lng"]
        if not timezone:
            timezone = resolved_location["tz_str"]
        if not country:
            country = resolved_location["country_code"]

    has_coordinates = latitude is not None and longitude is not None
    geonames_username = os.getenv("KERYKEION_GEONAMES_USERNAME")
    use_online = not (has_coordinates and bool(timezone))
    if use_online and not geonames_username:
        raise AstrologyError(
            "No se pudo resolver automaticamente la ubicacion de la ciudad. "
            "Intenta con una ciudad mas especifica (ej: 'Bogota, Cundinamarca') "
            "o define KERYKEION_GEONAMES_USERNAME como respaldo."
        )

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
        "nation": country,
        "country": country,
        "tz_str": timezone,
        "timezone": timezone,
        "lat": latitude,
        "lng": longitude,
        "lon": longitude,
        "geonames_username": geonames_username,
        "online": use_online,
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
