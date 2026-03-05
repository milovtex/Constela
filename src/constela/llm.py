from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LLMError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")

    def generate(self, model: str, prompt: str, temperature: float = 0.7) -> str:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            url=f"{self.base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=120) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            raise LLMError(f"Ollama devolvio HTTP {exc.code}.") from exc
        except URLError as exc:
            raise LLMError(
                "No se pudo conectar a Ollama. Verifica que este corriendo en localhost:11434."
            ) from exc
        except TimeoutError as exc:
            raise LLMError("Timeout consultando Ollama.") from exc

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise LLMError("Respuesta invalida desde Ollama.") from exc

        text = parsed.get("response")
        if not isinstance(text, str) or not text.strip():
            raise LLMError("Ollama no devolvio texto de interpretacion.")
        return text.strip()
