# AGENTS.md

## Proyecto

Nombre: Constela  
Tipo: CLI en Python para calculo de carta astral + interpretacion con LLM open source.

## Objetivo

Construir una herramienta de terminal que:

- Reciba datos natales del usuario.
- Calcule la carta astral con una libreria de astrologia.
- Genere una interpretacion en lenguaje natural con un LLM local.
- Entregue una experiencia CLI visualmente rica (colores, paneles, ASCII).

## Alcance MVP

- Comando `constela natal`.
- Flujo guiado para datos natales.
- Calculo de carta natal base.
- Prompt estructurado para interpretacion.
- Salida con formato enriquecido en terminal.

## Stack Base (actual)

- Python 3.11+
- Typer + Rich
- Kerykeion (motor astrologico)
- Ollama (runtime LLM local)
- Modelo sugerido inicial: Qwen3-8B

## Convenciones de trabajo

- Mantener codigo simple, legible y modular.
- Favorecer funciones pequenas y testeables.
- Evitar acoplar logica de dominio con presentacion CLI.
- Separar claramente:
  - Capa de entrada de datos
  - Capa de calculo astrologico
  - Capa de orquestacion de prompts/LLM
  - Capa de render en terminal

## Commits

Todos los commits del proyecto deben usar **Conventional Commits**.

Formato obligatorio:

`<type>(<scope>): <descripcion corta>`

Tipos recomendados:

- `feat`: nueva funcionalidad
- `fix`: correccion de bug
- `docs`: documentacion
- `refactor`: cambios internos sin alterar comportamiento externo
- `test`: pruebas
- `chore`: tareas de mantenimiento
- `build`: empaquetado/dependencias
- `ci`: pipelines/integracion continua

Ejemplos:

- `feat(cli): agregar comando natal interactivo`
- `feat(llm): integrar cliente de ollama`
- `fix(astrology): corregir manejo de zona horaria`
- `docs(readme): detallar alcance del mvp`

## Idioma y tono

- Documentacion y mensajes de usuario en espanol claro.
- Terminos tecnicos en ingles cuando sea estandar (CLI, prompt, runtime, etc).
