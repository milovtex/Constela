# Constela

Constela es una aplicacion CLI en Python para calcular cartas astrales y generar interpretaciones personalizadas usando un LLM open source.

## Contexto General

El objetivo del proyecto es combinar calculo astrologico estructurado con una experiencia de terminal moderna:

- Entrada guiada de datos natales (fecha, hora y lugar).
- Calculo de carta natal (planetas, casas y aspectos clave).
- Construccion de contexto en formato estructurado para el LLM.
- Interpretacion clara para usuario final en secciones utiles.
- Salida enriquecida en CLI con colores, paneles y ASCII.

## MVP

El primer entregable se enfoca en:

1. Comando principal `constela natal`.
2. Flujo interactivo para capturar datos natales.
3. Motor de calculo astrologico para carta natal.
4. Integracion con LLM local para interpretar resultados.
5. Render en terminal con una presentacion visual cuidada.

## Stack Inicial Propuesto

- Python 3.11+
- CLI: Typer + Rich
- Astrologia: Kerykeion
- LLM local: Ollama
- Modelo inicial sugerido: Qwen3-8B (ajustable segun hardware)

## Vision de Producto

Constela busca evolucionar de un lector de carta natal a un asistente astrologico CLI con modulos como:

- Transitos
- Sinastria
- Retorno solar
- Reportes exportables
- Historial de lecturas

## Estado

En fase inicial. Se esta definiendo arquitectura, alcance del MVP y experiencia de usuario en terminal.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
constela natal
```
