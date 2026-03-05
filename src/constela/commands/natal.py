from datetime import datetime

import typer
from rich.panel import Panel
from rich.table import Table

from constela.ui import console


natal_app = typer.Typer(help="Genera una lectura natal basica")


def _prompt_required(label: str) -> str:
    value = typer.prompt(label).strip()
    if not value:
        raise typer.BadParameter(f"{label} no puede estar vacio")
    return value


@natal_app.command("run")
def natal_run() -> None:
    """Flujo MVP de captura de datos natales e interpretacion placeholder."""
    console.print(Panel("Vamos a construir tu carta natal", border_style="cyan"))

    birth_date = _prompt_required("Fecha de nacimiento (YYYY-MM-DD)")
    birth_time = _prompt_required("Hora de nacimiento (HH:MM)")
    birth_city = _prompt_required("Ciudad de nacimiento")
    birth_country = _prompt_required("Pais de nacimiento")

    try:
        datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise typer.BadParameter(
            "Formato invalido. Usa YYYY-MM-DD y HH:MM"
        ) from exc

    table = Table(title="Datos natales", show_header=True, header_style="bold yellow")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="white")
    table.add_row("Fecha", birth_date)
    table.add_row("Hora", birth_time)
    table.add_row("Ciudad", birth_city)
    table.add_row("Pais", birth_country)
    console.print(table)

    console.print(
        Panel(
            "[bold green]MVP activo:[/bold green] calculo astrologico y motor LLM se conectaran en el siguiente paso.",
            title="Interpretacion",
            border_style="magenta",
        )
    )
