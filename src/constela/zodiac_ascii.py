from rich.panel import Panel

from constela.ui import console

ZODIAC_ASCII: dict[str, str] = {
    "aries": r"""
   .-.   .-.
  (_  \ /  _)
       |
       |
""".strip("\n"),
    "taurus": r"""
    .     .
    '.___.'
    .'   `.
   :       :
   :       :
    `.___.'
""".strip("\n"),
    "gemini": r"""
    ._____.
      | |
      | |
     _|_|_
    '     '
""".strip("\n"),
    "cancer": r"""
      .--.
     /   _`.
    (_) ( )
   '.    /
     `--'
""".strip("\n"),
    "leo": r"""
      .--.
     (    )
    (_)  /
        (_,
""".strip("\n"),
    "virgo": r"""
   _
  ' `:--.--.
     |  |  |_
     |  |  | )
     |  |  |/
          (J
""".strip("\n"),
    "libra": r"""
        __
   ___.'  '.___
   ____________
""".strip("\n"),
    "scorpio": r"""
   _
  ' `:--.--.
     |  |  |
     |  |  |
     |  |  |  ..,
           `---':
""".strip("\n"),
    "sagittarius": r"""
          ...
          .':
        .'
    `..'
    .'`.
""".strip("\n"),
    "capricorn": r"""
            _
    \      /_)
     \    /`.
      \  /   ;
       \/ __.'
""".strip("\n"),
    "aquarius": r"""
 .-"-._.-"-._.-
 .-"-._.-"-._.-
""".strip("\n"),
    "pisces": r"""
     `-.    .-'
        :  :
      --:--:--
        :  :
     .-'    `-.
""".strip("\n"),
}

_ALIASES = {
    "scorpius": "scorpio",
}


def normalize_sign(sign: str | None) -> str | None:
    if not sign:
        return None
    slug = sign.strip().lower()
    return _ALIASES.get(slug, slug)


def render_sign_ascii(sign: str | None, label: str) -> None:
    key = normalize_sign(sign)
    if not key:
        return
    art = ZODIAC_ASCII.get(key)
    if not art:
        return
    console.print(Panel.fit(art, title=label, border_style="bright_blue"))
