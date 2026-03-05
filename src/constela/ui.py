from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def render_banner() -> None:
    banner = Text(
        """
.d8888b.   .d88888b.  888b    888  .d8888b. 88888888888 8888888888 888             d8888
d88P  Y88b d88P" "Y88b 8888b   888 d88P  Y88b    888     888        888            d88888
888    888 888     888 88888b  888 Y88b.         888     888        888           d88P888
888        888     888 888Y88b 888  "Y888b.      888     8888888    888          d88P 888
888        888     888 888 Y88b888     "Y88b.    888     888        888         d88P  888
888    888 888     888 888  Y88888       "888    888     888        888        d88P   888
Y88b  d88P Y88b. .d88P 888   Y8888 Y88b  d88P    888     888        888       d8888888888
 "Y8888P"   "Y88888P"  888    Y888  "Y8888P"     888     8888888888 88888888 d88P     888
        """.strip("\n"),
        style="bold bright_cyan",
    )
    subtitle = Text(
        "🔮 Calcula tu carta natal y recibe una interpretación clara con un LLM local.",
        style="bold magenta",
    )
    steps = Text(
        "🧭 Flujo: datos natales → cálculo astrológico → lectura personalizada",
        style="bright_white",
    )
    console.print(
        Panel.fit(
            banner,
            border_style="bright_blue",
            title="✨ CONSTELA",
            subtitle="MVP CLI",
        )
    )
    console.print(subtitle)
    console.print(steps)
    console.print()
