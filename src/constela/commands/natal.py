from datetime import datetime

import typer
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from constela.astrology import AstrologyError, calculate_natal_chart, resolve_city_preview
from constela.llm import LLMError, OllamaClient
from constela.models import BirthData
from constela.prompting import build_interpretation_prompt
from constela.ui import console
from constela.zodiac_ascii import render_sign_ascii


def _prompt_required(label: str, hint: str) -> str:
    console.print(f"[bold bright_cyan]❓ {label}[/bold bright_cyan]")
    console.print(f"[dim]   {hint}[/dim]")
    value = console.input("[bold white]   ➤[/bold white]: ").strip()
    if not value:
        raise typer.BadParameter(f"{label} no puede estar vacio")
    console.print()
    return value


def natal_run(
    model: str = "qwen3:8b",
    ollama_url: str = "http://localhost:11434",
    no_ascii: bool = False,
) -> None:
    """Flujo MVP de captura de datos natales y lectura con LLM."""
    intro = Text.from_markup(
        "🌌 [bold]Lectura natal interactiva[/bold]\n"
        "Responde las preguntas con precisión para mejorar el cálculo astrológico.\n"
        "Con tu ciudad basta: la ubicación y zona horaria se resuelven automáticamente."
    )
    console.print(Panel(intro, title="🪐 constela natal", border_style="bright_blue"))
    console.print()

    name = _prompt_required("Nombre para la lectura", "Cómo quieres que te llame en la interpretación.")
    birth_date = _prompt_required("Fecha de nacimiento (YYYY-MM-DD)", "Ejemplo: 1997-08-21")
    birth_time = _prompt_required("Hora de nacimiento (HH:MM)", "Formato 24h. Ejemplo: 07:45")
    birth_city = _prompt_required("Ciudad de nacimiento", "Ejemplo: Medellín")

    try:
        datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise typer.BadParameter(
            "Formato invalido. Usa YYYY-MM-DD y HH:MM"
        ) from exc

    resolved_location = resolve_city_preview(city=birth_city)
    if resolved_location is not None:
        detected = Table(title="📍 Ubicación detectada", show_header=True, header_style="bold green")
        detected.add_column("Campo", style="bright_green")
        detected.add_column("Valor", style="white")
        detected.add_row("🏙️ Ciudad", str(resolved_location.get("city") or birth_city))
        detected.add_row("🌎 País", str(resolved_location.get("country_code") or "-"))
        detected.add_row("🕓 Zona horaria", str(resolved_location.get("tz_str") or "-"))
        console.print(detected)

        if not typer.confirm("¿Usar esta ubicación detectada?", default=True):
            console.print(
                Panel(
                    "Lectura cancelada. Intenta con una ciudad más específica para mejorar la detección.",
                    title="ℹ️ Constela",
                    border_style="yellow",
                )
            )
            raise typer.Exit(code=1)

    birth_data = BirthData(
        name=name,
        birth_date=birth_date,
        birth_time=birth_time,
        city=birth_city,
        country=None if resolved_location is None else (resolved_location.get("country_code") or None),
        timezone=None if resolved_location is None else (resolved_location.get("tz_str") or None),
        latitude=None if resolved_location is None else float(resolved_location["lat"]),
        longitude=None if resolved_location is None else float(resolved_location["lng"]),
    )

    table = Table(title="🧾 Datos natales capturados", show_header=True, header_style="bold yellow")
    table.add_column("Campo", style="bright_cyan")
    table.add_column("Valor", style="white")
    table.add_row("👤 Nombre", name)
    table.add_row("📅 Fecha", birth_date)
    table.add_row("⏰ Hora", birth_time)
    table.add_row("🏙️ Ciudad", birth_city)
    console.print(table)

    with console.status("[bold cyan]🧮 Calculando carta natal...[/bold cyan]"):
        try:
            chart = calculate_natal_chart(birth_data)
        except AstrologyError as exc:
            console.print(
                Panel(
                    f"[bold red]Error astrológico:[/bold red] {exc}",
                    title="🚫 Constela",
                    border_style="red",
                )
            )
            raise typer.Exit(code=1)

    summary = Table(title="🔭 Resumen de carta natal", show_header=True, header_style="bold magenta")
    summary.add_column("Elemento", style="bright_cyan")
    summary.add_column("Signo", style="white")
    summary.add_column("Casa", style="white")

    if chart.sun:
        summary.add_row("☀️ Sol", chart.sun.sign or "-", chart.sun.house or "-")
    if chart.moon:
        summary.add_row("🌙 Luna", chart.moon.sign or "-", chart.moon.house or "-")
    summary.add_row("⬆️ Ascendente", chart.ascendant or "-", "-")
    console.print(summary)

    planets = [p for p in chart.planets if p.sign]
    if planets:
        planets_table = Table(title="🪐 Planetas principales", show_header=True, header_style="bold bright_blue")
        planets_table.add_column("Planeta", style="bright_magenta")
        planets_table.add_column("Signo", style="white")
        planets_table.add_column("Casa", style="white")
        for p in planets:
            planets_table.add_row(p.planet, p.sign or "-", p.house or "-")
        console.print(planets_table)

    if not no_ascii:
        console.print(Panel("[bold bright_white]✨ Arte ASCII de tus signos clave[/bold bright_white]", border_style="bright_magenta"))
        if chart.sun:
            render_sign_ascii(chart.sun.sign, "Sol")
        if chart.moon:
            render_sign_ascii(chart.moon.sign, "Luna")
        render_sign_ascii(chart.ascendant, "Ascendente")

    prompt = build_interpretation_prompt(birth_data, chart)
    llm_client = OllamaClient(base_url=ollama_url)

    with console.status("[bold cyan]🤖 Generando interpretación con LLM...[/bold cyan]"):
        try:
            interpretation = llm_client.generate(model=model, prompt=prompt)
        except LLMError as exc:
            console.print(
                Panel(
                    f"[bold red]Error de LLM:[/bold red] {exc}\n\n"
                    "Asegurate de tener Ollama arriba y el modelo descargado.\n"
                    f"Ejemplo: [bold]ollama pull {model}[/bold]",
                    title="🚫 Constela",
                    border_style="red",
                )
            )
            raise typer.Exit(code=1)

    console.print(Panel("[bold green]✅ Lectura generada[/bold green]", border_style="green"))
    console.print(Markdown(interpretation))
    console.print(
        Panel(
            "\n".join(
                [
                    "💬 [bold]Sugerencias para seguir conversando con el LLM[/bold]",
                    "",
                    "1. ¿Cuál es el equilibrio entre mi Sol, Luna y Ascendente?",
                    "2. ¿Qué patrones emocionales se ven en mi Luna y cómo trabajarlos?",
                    "3. ¿Qué áreas de vida se activan más según mis casas principales?",
                    "4. Dame recomendaciones prácticas para esta semana según mi carta.",
                    "5. Explica mi carta en tono breve, directo y accionable.",
                ]
            ),
            title="🧠 Próximas preguntas",
            border_style="bright_green",
        )
    )
