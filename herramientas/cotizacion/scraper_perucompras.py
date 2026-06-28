#!/usr/bin/env python3
"""Scraper HTML para el buscador publico de catalogos de PeruCompras."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
    from bs4 import BeautifulSoup
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.table import Table
except ImportError as exc:  # pragma: no cover - fallo temprano de entorno.
    print(
        "[error] Falta una dependencia. Instala: pip install requests beautifulsoup4 rich",
        file=sys.stderr,
    )
    print(f"[error] Modulo faltante: {exc.name}", file=sys.stderr)
    sys.exit(1)


BASE_URL = "https://buscadorcatalogos.perucompras.gob.pe/"
REQUEST_TIMEOUT = 30
DELAY_SECONDS = 2.0
DEFAULT_KEY = "item"
NO_ENCONTRADO = "NO_ENCONTRADO"

console = Console()


class CriticalScraperError(RuntimeError):
    """Error que impide continuar con el scraping completo."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Busca materiales de un BOM JSON en el buscador publico de "
            "catalogos de PeruCompras y guarda resultados en JSON."
        )
    )
    parser.add_argument("--input", required=True, help="Ruta del JSON de entrada.")
    parser.add_argument("--output", required=True, help="Ruta del JSON de salida.")
    parser.add_argument(
        "--key",
        default=DEFAULT_KEY,
        help="Llave donde esta el nombre del material dentro del BOM. Por defecto: item.",
    )
    return parser.parse_args()


def clean_text(value: Any) -> str:
    text = "" if value is None else str(value)
    return re.sub(r"\s+", " ", text).strip()


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise CriticalScraperError(f"No existe el archivo de entrada: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CriticalScraperError(f"JSON invalido en {path}: {exc}") from exc
    except OSError as exc:
        raise CriticalScraperError(f"No se pudo leer {path}: {exc}") from exc


def unwrap_items(raw: Any) -> list[dict[str, Any]]:
    """Acepta lista directa o contenedores comunes de BOM."""
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        for key in ("materiales", "items", "data", "rows", "resultados"):
            value = raw.get(key)
            if isinstance(value, list):
                items = value
                break
        else:
            items = [raw]
    else:
        raise CriticalScraperError("El JSON debe ser una lista o un objeto con materiales/items/data.")

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        if isinstance(item, dict):
            normalized.append(item)
        else:
            normalized.append({"item": str(item), "_source_index": index})
    return normalized


def get_material_query(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if value is None or not str(value).strip():
        raise ValueError(f"El item no tiene valor util en la llave '{key}'.")
    return clean_text(value)


def extract_form_state(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    form = soup.select_one("form#form-search") or soup.select_one("form[method]")
    if not form:
        raise CriticalScraperError("No se encontro el formulario de busqueda en PeruCompras.")

    payload: dict[str, str] = {}
    for field in form.select("input[name]"):
        name = field.get("name")
        if name:
            payload[name] = field.get("value", "")

    token = payload.get("__RequestVerificationToken")
    if not token:
        raise CriticalScraperError("No se encontro __RequestVerificationToken en el formulario.")
    return payload


def bootstrap_session() -> tuple[requests.Session, dict[str, str]]:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
        }
    )

    try:
        response = session.get(BASE_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise CriticalScraperError(f"No se pudo abrir PeruCompras: {exc}") from exc

    if not session.cookies:
        raise CriticalScraperError("El GET inicial no entrego cookies de sesion.")
    return session, extract_form_state(response.text)


def build_search_payload(base_payload: dict[str, str], query: str) -> dict[str, str]:
    payload = dict(base_payload)
    payload.update(
        {
            "From": payload.get("From") or "Search",
            "IsNewSearch": "True",
            "SearchText": query,
            "Status": "VIGENTE",
            "Pagination.Page": "0",
            "Pagination.Paging": "0",
            "Pagination.LeftMostPage": "0",
        }
    )
    payload.setdefault("ClientFilter.Feature", "[]")
    return payload


def update_token_from_response(base_payload: dict[str, str], html: str) -> dict[str, str]:
    try:
        new_payload = extract_form_state(html)
    except CriticalScraperError:
        return base_payload
    token = new_payload.get("__RequestVerificationToken")
    if token:
        base_payload["__RequestVerificationToken"] = token
    return base_payload


def post_search(session: requests.Session, base_payload: dict[str, str], query: str) -> requests.Response:
    headers = {
        "Origin": "https://buscadorcatalogos.perucompras.gob.pe",
        "Referer": BASE_URL,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = session.post(
        BASE_URL,
        data=build_search_payload(base_payload, query),
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response


def html_to_plain_text(html_fragment: str) -> str:
    if not html_fragment:
        return ""
    return clean_text(BeautifulSoup(html_fragment, "html.parser").get_text(" ", strip=True))


def parse_cards(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    cards: list[dict[str, str]] = []
    for link in soup.select("[data-fp]"):
        cards.append(
            {
                "nombre_oficial": clean_text(link.get("data-fp")),
                "categoria": clean_text(link.get("data-category")),
                "catalogo": clean_text(link.get("data-catalogue")),
                "acuerdo_marco": clean_text(link.get("data-agreement")),
                "estado_ficha": clean_text(link.get("data-status")),
                "fecha_publicacion": clean_text(link.get("data-published-date")),
                "fecha_actualizacion": clean_text(link.get("data-updated-date")),
                "url_imagen": clean_text(link.get("data-img")),
                "url_ficha_pdf": clean_text(link.get("data-file")),
                "caracteristicas": html_to_plain_text(link.get("data-feature", "")),
            }
        )
    return [card for card in cards if card["nombre_oficial"]]


def extract_result_message(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    patterns = (
        r"No se han encontrado fichas-producto\.?",
        r"Se han encontrado\s+\d+\s+fichas-producto",
        r"Se han encontrado\s+\d+\s+fichas",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(0))
    return ""


def is_no_result(html: str) -> bool:
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True).lower()
    return (
        "no se han encontrado fichas-producto" in text
        or "se han encontrado 0 fichas" in text
    )


def search_one(
    session: requests.Session,
    base_payload: dict[str, str],
    index: int,
    item: dict[str, Any],
    key: str,
) -> dict[str, Any]:
    query = get_material_query(item, key)
    response = post_search(session, base_payload, query)
    update_token_from_response(base_payload, response.text)

    cards = parse_cards(response.text)
    message = extract_result_message(response.text)
    if not cards or is_no_result(response.text):
        return {
            "index": index,
            "input_key": key,
            "query": query,
            "status": NO_ENCONTRADO,
            "mensaje": message or "No se detectaron tarjetas de resultados.",
            "nombre_oficial": "",
            "primer_resultado": None,
            "resultados_visibles": 0,
            "resultados": [],
            "error": "",
        }

    first = cards[0]
    return {
        "index": index,
        "input_key": key,
        "query": query,
        "status": "OK",
        "mensaje": message,
        "nombre_oficial": first["nombre_oficial"],
        "primer_resultado": first,
        "resultados_visibles": len(cards),
        "resultados": cards,
        "error": "",
    }


def write_output(path: Path, payload: dict[str, Any]) -> None:
    if path.suffix.lower() != ".json":
        raise CriticalScraperError("La salida debe ser un archivo .json.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def render_summary(results: list[dict[str, Any]]) -> None:
    total = len(results)
    ok = sum(1 for row in results if row.get("status") == "OK")
    not_found = sum(1 for row in results if row.get("status") == NO_ENCONTRADO)
    errors = sum(1 for row in results if row.get("status") == "ERROR")

    table = Table(title="Resumen PeruCompras")
    table.add_column("Total", justify="right")
    table.add_column("OK", justify="right", style="green")
    table.add_column("NO_ENCONTRADO", justify="right", style="yellow")
    table.add_column("ERROR", justify="right", style="red")
    table.add_row(str(total), str(ok), str(not_found), str(errors))
    console.print(table)


def run(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    output_path = Path(args.output)
    items = unwrap_items(load_json(input_path))

    console.rule("[bold cyan]Scraper PeruCompras")
    console.print(f"[cyan]Input:[/] {input_path}")
    console.print(f"[cyan]Output:[/] {output_path}")
    console.print(f"[cyan]Items:[/] {len(items)}")

    session, base_payload = bootstrap_session()
    console.print("[green]Sesion iniciada; cookies y token anti-forgery capturados.[/]")

    results: list[dict[str, Any]] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Buscando materiales", total=len(items))
        for index, item in enumerate(items, start=1):
            try:
                row = search_one(session, base_payload, index, item, args.key)
                if row["status"] == "OK":
                    console.print(f"[green]OK[/] {index}: {row['query']} -> {row['nombre_oficial'][:90]}")
                else:
                    console.print(f"[yellow]{NO_ENCONTRADO}[/] {index}: {row['query']}")
            except Exception as exc:
                row = {
                    "index": index,
                    "input_key": args.key,
                    "query": clean_text(item.get(args.key, "")) if isinstance(item, dict) else "",
                    "status": "ERROR",
                    "mensaje": "",
                    "nombre_oficial": "",
                    "primer_resultado": None,
                    "resultados_visibles": 0,
                    "resultados": [],
                    "error": str(exc),
                }
                console.print(f"[yellow]Advertencia[/] item {index}: {exc}")
            results.append(row)
            progress.advance(task)
            if index < len(items):
                time.sleep(DELAY_SECONDS)

    output_payload = {
        "metadata": {
            "fuente": BASE_URL,
            "generado_en": datetime.now(timezone.utc).isoformat(),
            "input": str(input_path),
            "output": str(output_path),
            "key": args.key,
            "delay_seconds": DELAY_SECONDS,
            "total_items": len(items),
            "status_default": "VIGENTE",
        },
        "resumen": {
            "ok": sum(1 for row in results if row.get("status") == "OK"),
            "no_encontrado": sum(1 for row in results if row.get("status") == NO_ENCONTRADO),
            "error": sum(1 for row in results if row.get("status") == "ERROR"),
        },
        "resultados": results,
    }
    write_output(output_path, output_payload)
    render_summary(results)
    console.print(f"[green]JSON guardado:[/] {output_path}")
    return 0


def main() -> int:
    args = parse_args()
    try:
        return run(args)
    except CriticalScraperError as exc:
        console.print(f"[red]Error critico:[/] {exc}", stderr=True)
        return 1
    except requests.RequestException as exc:
        console.print(f"[red]Error de red:[/] {exc}", stderr=True)
        return 1
    except KeyboardInterrupt:
        console.print("[yellow]Ejecucion interrumpida por el usuario.[/]", stderr=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
