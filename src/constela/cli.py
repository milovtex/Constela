import typer

from constela.commands.natal import natal_run
from constela.ui import render_banner

app = typer.Typer(
    help="CLI para calcular e interpretar cartas astrales con LLM open source",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Punto de entrada principal para la CLI."""
    render_banner()


@app.command("natal")
def natal() -> None:
    """Inicia el flujo de carta natal del MVP."""
    natal_run()


if __name__ == "__main__":
    app()
