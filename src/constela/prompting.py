import json

from constela.models import BirthData, ChartSummary


def build_interpretation_prompt(data: BirthData, chart: ChartSummary) -> str:
    payload = {
        "birth_data": {
            "name": data.name,
            "birth_date": data.birth_date,
            "birth_time": data.birth_time,
            "city": data.city,
            "country": data.country,
            "timezone": data.timezone,
            "latitude": data.latitude,
            "longitude": data.longitude,
        },
        "chart_summary": {
            "sun": None if chart.sun is None else {"sign": chart.sun.sign, "house": chart.sun.house},
            "moon": None if chart.moon is None else {"sign": chart.moon.sign, "house": chart.moon.house},
            "ascendant": chart.ascendant,
            "planets": [{"planet": p.planet, "sign": p.sign, "house": p.house} for p in chart.planets],
        },
    }

    return (
        "Eres un interprete astrologico profesional. Responde en espanol claro, cercano y sin fatalismo.\n"
        "Usa SOLO los datos entregados. Si falta informacion, dilo explicitamente.\n"
        "Estructura la respuesta con estos titulos:\n"
        "1) Identidad (Sol, Luna, Ascendente)\n"
        "2) Vinculos y afecto\n"
        "3) Vocacion y trabajo\n"
        "4) Fortalezas y retos\n"
        "5) Recomendaciones practicas (3 acciones concretas)\n\n"
        "Datos:\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )
