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
def natal(
    model: str = typer.Option("qwen3:8b", "--model", help="Modelo disponible en Ollama"),
    ollama_url: str = typer.Option("http://localhost:11434", "--ollama-url", help="URL base de Ollama"),
    no_ascii: bool = typer.Option(False, "--no-ascii", help="Desactiva el arte ASCII de signos"),
) -> None:
    """Inicia el flujo de carta natal del MVP."""
    natal_run(model=model, ollama_url=ollama_url, no_ascii=no_ascii)


if __name__ == "__main__":
    app()
