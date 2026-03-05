from datetime import datetime

import typer
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from constela.astrology import AstrologyError, calculate_natal_chart
from constela.llm import LLMError, OllamaClient
from constela.models import BirthData
from constela.prompting import build_interpretation_prompt
from constela.ui import console


def _prompt_required(label: str) -> str:
    value = typer.prompt(label).strip()
    if not value:
        raise typer.BadParameter(f"{label} no puede estar vacio")
    return value


def _prompt_float_or_empty(label: str) -> float | None:
    value = typer.prompt(label, default="").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise typer.BadParameter(f"{label} debe ser numero decimal") from exc


@natal_app.command("run")
def natal_run(
    model: str = typer.Option("qwen3:8b", "--model", help="Modelo disponible en Ollama"),
    ollama_url: str = typer.Option("http://localhost:11434", "--ollama-url", help="URL base de Ollama"),
) -> None:
    """Flujo MVP de captura de datos natales y lectura con LLM."""
    console.print(Panel("Vamos a construir tu carta natal", border_style="cyan"))

    name = _prompt_required("Nombre para la lectura")
    birth_date = _prompt_required("Fecha de nacimiento (YYYY-MM-DD)")
    birth_time = _prompt_required("Hora de nacimiento (HH:MM)")
    birth_city = _prompt_required("Ciudad de nacimiento")
    birth_country = _prompt_required("Pais de nacimiento")
    timezone = _prompt_required("Zona horaria IANA (ej. America/Bogota)")
    latitude = _prompt_float_or_empty("Latitud (opcional, Enter para omitir)")
    longitude = _prompt_float_or_empty("Longitud (opcional, Enter para omitir)")

    try:
        datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise typer.BadParameter(
            "Formato invalido. Usa YYYY-MM-DD y HH:MM"
        ) from exc

    birth_data = BirthData(
        name=name,
        birth_date=birth_date,
        birth_time=birth_time,
        city=birth_city,
        country=birth_country,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
    )

    table = Table(title="Datos natales", show_header=True, header_style="bold yellow")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="white")
    table.add_row("Nombre", name)
    table.add_row("Fecha", birth_date)
    table.add_row("Hora", birth_time)
    table.add_row("Ciudad", birth_city)
    table.add_row("Pais", birth_country)
    table.add_row("Zona horaria", timezone)
    table.add_row("Latitud", "-" if latitude is None else str(latitude))
    table.add_row("Longitud", "-" if longitude is None else str(longitude))
    console.print(table)

    with console.status("[bold cyan]Calculando carta natal...[/bold cyan]"):
        try:
            chart = calculate_natal_chart(birth_data)
        except AstrologyError as exc:
            console.print(
                Panel(
                    f"[bold red]Error astrologico:[/bold red] {exc}",
                    title="Constela",
                    border_style="red",
                )
            )
            raise typer.Exit(code=1)

    summary = Table(title="Resumen de carta", show_header=True, header_style="bold magenta")
    summary.add_column("Elemento", style="cyan")
    summary.add_column("Signo", style="white")
    summary.add_column("Casa", style="white")

    if chart.sun:
        summary.add_row("Sol", chart.sun.sign or "-", chart.sun.house or "-")
    if chart.moon:
        summary.add_row("Luna", chart.moon.sign or "-", chart.moon.house or "-")
    summary.add_row("Ascendente", chart.ascendant or "-", "-")
    console.print(summary)

    prompt = build_interpretation_prompt(birth_data, chart)
    llm_client = OllamaClient(base_url=ollama_url)

    with console.status("[bold cyan]Generando interpretacion con LLM...[/bold cyan]"):
        try:
            interpretation = llm_client.generate(model=model, prompt=prompt)
        except LLMError as exc:
            console.print(
                Panel(
                    f"[bold red]Error de LLM:[/bold red] {exc}\n\n"
                    "Asegurate de tener Ollama arriba y el modelo descargado.\n"
                    f"Ejemplo: [bold]ollama pull {model}[/bold]",
                    title="Constela",
                    border_style="red",
                )
            )
            raise typer.Exit(code=1)

    console.print(Panel("[bold green]Lectura generada[/bold green]", border_style="green"))
    console.print(Markdown(interpretation))
