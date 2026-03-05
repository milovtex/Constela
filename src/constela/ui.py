from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def render_banner() -> None:
    banner = Text(
        """
  ______                __       __      
 / ____/___  ____  _____/ /____  / /___ _ 
/ /   / __ \/ __ \/ ___/ __/ _ \/ / __ `/ 
/ /___/ /_/ / / / (__  ) /_/  __/ / /_/ /  
\____/\____/_/ /_/____/\__/\___/_/\__,_/   
        """.rstrip("\n"),
        style="bold cyan",
    )
    subtitle = Text("Carta astral + interpretacion con LLM", style="magenta")
    console.print(Panel.fit(banner, border_style="blue", title="Constela"))
    console.print(subtitle)
