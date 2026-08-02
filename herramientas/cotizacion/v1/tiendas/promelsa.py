#!/usr/bin/env python3
"""Agente de compras Promelsa para el modulo de cotizacion.

El script esta pensado para ser reusable entre proyectos: no asume rutas del
Proyecto Aquiles ni una estructura unica de JSON. Recibe la ruta del BOM por
CLI, detecta listas comunes de materiales y agrega una cotizacion Promelsa a
cada item procesado.

Implementacion real de la tienda Promelsa. La entrada recomendada para
operadores y agentes externos es `v1/cli/promelsa.py`; este archivo tambien se
puede ejecutar directamente para depuracion:

    python3 herramientas/cotizacion/v1/tiendas/promelsa.py \
      --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
      --output build/aquiles_promelsa.json \
      --modo cli \
      --key item
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import unicodedata
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup


PROMELSA_BASE_URL = "https://www.promelsa.com.pe/"
PROMELSA_SEARCH_URL = (
    "https://www.promelsa.com.pe/catalogsearch/result/?q={termino_de_busqueda}"
)
DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRIES = 3
DEFAULT_DELAY_SECONDS = 0.8
DEFAULT_MAX_CANDIDATES = 5
DEFAULT_GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

LIST_KEYS = (
    "materiales",
    "items",
    "data",
    "rows",
    "resultados",
    "presupuesto_recomendado",
    "comparativa",
)
QUERY_KEYS = ("item", "material", "nombre", "descripcion", "producto")
STOPWORDS = {
    "a",
    "al",
    "con",
    "contra",
    "de",
    "del",
    "e",
    "el",
    "en",
    "la",
    "las",
    "los",
    "para",
    "por",
    "tipo",
    "un",
    "una",
    "y",
}
SECONDARY_WORDS = {
    "alimentador",
    "auxiliar",
    "circuito",
    "general",
    "instalacion",
    "monofasico",
    "piso",
    "principal",
    "proteccion",
    "salida",
    "servicio",
    "trifasico",
    "vivienda",
}


class AgenteComprasError(RuntimeError):
    """Error controlado del agente de compras."""


@dataclass(frozen=True)
class SearchResult:
    candidatos: list[dict[str, Any]]
    consultas_intentadas: list[str]
    consulta_usada: str | None
    busqueda_relajada: bool


def eprint(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Busca materiales en Promelsa y actualiza un JSON/BOM con precio, "
            "SKU, ficha tecnica y evidencia de seleccion."
        )
    )
    parser.add_argument("--input", required=True, help="Ruta del JSON de entrada.")

    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument("--output", help="Ruta del JSON actualizado.")
    output_group.add_argument(
        "--in-place",
        action="store_true",
        help="Sobrescribe el archivo de entrada con el JSON actualizado.",
    )

    parser.add_argument(
        "--modo",
        choices=("heuristico", "auto", "cli"),
        default="cli",
        help=(
            "heuristico selecciona solo coincidencias tecnicas fuertes sin API; "
            "auto usa Gemini API; cli espera una opcion por stdin."
        ),
    )
    parser.add_argument(
        "--key",
        default="item",
        help="Llave primaria del nombre del material dentro de cada item. Por defecto: item.",
    )
    parser.add_argument(
        "--items-path",
        help=(
            "Ruta con puntos hacia la lista de materiales, por ejemplo "
            "'materiales' o 'presupuesto.items'. Si se omite, se autodetecta."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Procesa solo los primeros N materiales encontrados.",
    )
    parser.add_argument(
        "--max-candidatos",
        type=int,
        default=DEFAULT_MAX_CANDIDATES,
        help=f"Cantidad maxima de candidatos Promelsa. Por defecto: {DEFAULT_MAX_CANDIDATES}.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help=f"Segundos de espera entre materiales. Por defecto: {DEFAULT_DELAY_SECONDS}.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Consultas concurrentes independientes (1 a 6). Por defecto: 1.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout HTTP por request. Por defecto: {DEFAULT_TIMEOUT}.",
    )
    parser.add_argument(
        "--reintentos",
        type=int,
        default=DEFAULT_RETRIES,
        help=f"Reintentos ante fallos temporales de red. Por defecto: {DEFAULT_RETRIES}.",
    )
    parser.add_argument(
        "--modelo-gemini",
        default=DEFAULT_GEMINI_MODEL,
        help=(
            "Modelo Gemini para --modo auto. Tambien puede definirse con "
            f"GEMINI_MODEL. Por defecto: {DEFAULT_GEMINI_MODEL}."
        ),
    )
    parser.add_argument(
        "--gemini-reintentos",
        type=int,
        default=3,
        help="Reintentos ante errores temporales o 429 de Gemini. Por defecto: 3.",
    )
    parser.add_argument(
        "--gemini-backoff",
        type=float,
        default=8.0,
        help="Espera base en segundos para reintentos Gemini si la API no indica retry_delay.",
    )
    parser.add_argument(
        "--env-file",
        help=(
            "Ruta a un archivo .env. Si se omite, se buscan .env en la raiz "
            "del proyecto, junto al JSON y en herramientas/cotizacion."
        ),
    )
    parser.add_argument(
        "--formato-cli",
        choices=("json", "lista"),
        default="json",
        help="Formato de candidatos en modo cli. Por defecto: json.",
    )
    parser.add_argument(
        "--no-actualizar-precio",
        action="store_true",
        help="Agrega la cotizacion Promelsa sin tocar precio_unit_soles/costo_soles.",
    )
    return parser.parse_args(argv)


def clean_text(value: Any) -> str:
    text = "" if value is None else str(value)
    return re.sub(r"\s+", " ", text).strip()


def remove_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_text(value: str) -> str:
    text = remove_accents(clean_text(value)).lower()
    replacements = {
        "mm²": "mm2",
        "mm^2": "mm2",
        "m²": "m2",
        "”": '"',
        "“": '"',
        "’": "'",
        "´": "'",
        "`": "'",
        "ø": " diametro ",
        "φ": " diametro ",
        "–": "-",
        "—": "-",
        "×": " x ",
        "*": " x ",
        "¨": '"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\b(\d+)\s*p\b", r"\1 p", text)
    text = re.sub(r"\b(\d+(?:[.,]\d+)?)\s*mm\s*2\b", r"\1 mm2", text)
    text = re.sub(r"\b(\d+(?:[.,]\d+)?)\s*mm2\b", r"\1 mm2", text)
    text = re.sub(r"\b(\d+(?:[.,]\d+)?)\s*mm\b", r"\1 mm", text)
    text = re.sub(r"\b(\d+(?:[.,]\d+)?)\s*ma\b", r"\1 ma", text)
    text = re.sub(r"\b(\d+(?:[.,]\d+)?)\s*a\b", r"\1 a", text)
    text = re.sub(r"\b(\d+(?:[.,]\d+)?)\s*w\b", r"\1 w", text)
    text = re.sub(r"[\\|_+,:;()\[\]{}]", " ", text)
    text = re.sub(r"\s*-\s*", " ", text)
    text = re.sub(r"[^a-z0-9. /\"'-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sanitize_query(value: str) -> str:
    text = normalize_text(value)
    return re.sub(r"\s+", " ", text).strip()


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = sanitize_query(value)
        key = normalize_text(cleaned)
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def ordered_unique_raw(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = clean_text(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def relaxed_search_queries(material_name: str) -> list[str]:
    """Genera busquedas mas amplias si Promelsa no devuelve resultados."""
    text = normalize_text(material_name)
    text = re.sub(r"\b(?:c|circuito)\s*\d+\b", " ", text)
    text = re.sub(r"\b\d+(?:er|do|ro)?\s*piso\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = [
        token
        for token in re.findall(r"[a-z0-9.]+", text)
        if token not in STOPWORDS and token not in SECONDARY_WORDS
    ]

    section = re.search(r"\b(\d+(?:[.]\d+)?)\s*mm2\b", text)
    diameter = re.search(r"\b(\d+(?:[.]\d+)?)\s*mm\b", text)
    watts = re.search(r"\b(\d+(?:[.]\d+)?)\s*w\b", text)
    amps = re.search(r"\b(\d+(?:[.]\d+)?)\s*a\b", text)
    milliamps = re.search(r"\b(\d+(?:[.]\d+)?)\s*ma\b", text)
    poles = re.search(r"\b(\d+)\s*p\b|\b(\d+)\s*polos?\b", text)
    circuits = re.search(r"\b(\d+)\s*circuitos?\b", text)

    variants: list[str] = []
    compact = " ".join(tokens)
    if compact:
        variants.append(compact)
        variants.append(" ".join(tokens[:4]))

    if "cable" in text or "conductor" in text or "thw" in text or "tw" in text:
        cable_type = "thw" if "thw" in text else "tw" if "tw" in text else ""
        if section:
            variants.append(f"cable {cable_type} {section.group(1)} mm2")
        variants.append("cable electrico")
    if "tubo" in text or "tuberia" in text or "pvc" in text:
        if diameter:
            variants.append(f"tubo pvc {diameter.group(1)} mm")
        variants.extend(["tubo pvc sap", "tubo pvc"])
    if "curva" in text and "pvc" in text:
        if diameter:
            variants.append(f"curva pvc {diameter.group(1)} mm")
        variants.append("curva pvc sap")
    if "union" in text and "pvc" in text:
        if diameter:
            variants.append(f"union pvc {diameter.group(1)} mm")
        variants.append("union pvc sap")
    if "termomagnetico" in text or "itm" in text:
        poles_value = poles.group(1) or poles.group(2) if poles else ""
        amps_value = amps.group(1) if amps else ""
        spec = " ".join(
            part
            for part in [
                f"{poles_value}p" if poles_value else "",
                f"{amps_value}a" if amps_value else "",
            ]
            if part
        )
        if poles_value and amps_value:
            variants.append(f"interruptor termomagnetico {poles_value}x{amps_value}a")
            variants.append(f"interruptor termomagnetico {poles_value}x{amps_value}")
        variants.append(f"interruptor termomagnetico {spec}".strip())
        variants.append("interruptor termomagnetico")
    if "diferencial" in text:
        poles_value = poles.group(1) or poles.group(2) if poles else ""
        amps_value = amps.group(1) if amps else ""
        milliamps_value = milliamps.group(1) if milliamps else ""
        spec = " ".join(
            part
            for part in [
                f"{poles_value}p" if poles_value else "",
                f"{amps_value}a" if amps_value else "",
                f"{milliamps_value}ma" if milliamps_value else "",
            ]
            if part
        )
        if poles_value and amps_value:
            variants.append(f"interruptor diferencial {poles_value}x{amps_value}a")
            variants.append(f"diferencial {poles_value}x{amps_value}a")
        variants.append(f"interruptor diferencial {spec}".strip())
        variants.append("diferencial")
    if "tablero" in text:
        if circuits:
            variants.append(f"tablero {circuits.group(1)} circuitos")
        variants.append("tablero electrico")
    if "led" in text or "foco" in text or "lampara" in text or "luminaria" in text:
        if watts:
            variants.append(f"foco led {watts.group(1)}w")
            variants.append(f"lampara led {watts.group(1)}w")
        variants.extend(["luminaria led", "foco led"])
    if "tomacorriente" in text or "toma corriente" in text:
        variants.extend(["tomacorriente", "tomacorriente doble"])
    if "caja" in text:
        variants.extend(["caja electrica", "caja pase", "caja rectangular"])
    if "cinta" in text and "aisl" in text:
        variants.extend(["cinta aislante", "cinta electrica"])

    return ordered_unique(variants)


def parse_price(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"(\d[\d.,]*)", value.replace("\xa0", " "))
    if not match:
        return None
    number = match.group(1)
    if "." in number and "," in number:
        if number.rfind(".") > number.rfind(","):
            number = number.replace(",", "")
        else:
            number = number.replace(".", "").replace(",", ".")
    elif "," in number:
        decimals = number.rsplit(",", 1)[-1]
        number = number.replace(",", ".") if len(decimals) <= 2 else number.replace(",", "")
    try:
        price = float(number)
    except ValueError:
        return None
    if price <= 0:
        return None
    return round(price, 2)


def parse_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = clean_text(value).replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
        }
    )
    return session


def parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()
    if "=" not in stripped:
        return None
    name, value = stripped.split("=", 1)
    name = name.strip()
    value = value.strip()
    if not name:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return name, value


def load_env_file(path: Path, *, override: bool = False) -> list[str]:
    loaded: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return loaded
    except OSError as exc:
        raise AgenteComprasError(f"No se pudo leer .env en {path}: {exc}") from exc

    for line in lines:
        parsed = parse_env_line(line)
        if not parsed:
            continue
        name, value = parsed
        if override or name not in os.environ:
            os.environ[name] = value
            loaded.append(name)

    aliases = {
        "api_key_de_gemini": "GEMINI_API_KEY",
        "GEMINI_KEY": "GEMINI_API_KEY",
        "GEMINI_APIKEY": "GEMINI_API_KEY",
        "GOOGLE_API_KEY": "GEMINI_API_KEY",
    }
    for source, target in aliases.items():
        if source in os.environ and (override or target not in os.environ):
            os.environ[target] = os.environ[source]
            loaded.append(target)
    return loaded


def discover_env_files(input_path: Path, explicit_env_file: str | None) -> list[Path]:
    if explicit_env_file:
        return [Path(explicit_env_file).expanduser().resolve()]

    script_dir = Path(__file__).resolve().parent
    candidates = [Path.cwd() / ".env", input_path.parent / ".env", input_path.parent.parent / ".env"]
    for directory in [script_dir, *script_dir.parents]:
        candidates.append(directory / ".env")
    seen: set[Path] = set()
    result: list[Path] = []
    for path in candidates:
        resolved = path.expanduser().resolve()
        if resolved not in seen and resolved.exists():
            seen.add(resolved)
            result.append(resolved)
    return result


def load_environment(args: argparse.Namespace, input_path: Path) -> list[Path]:
    loaded_paths: list[Path] = []
    for env_path in discover_env_files(input_path, args.env_file):
        names = load_env_file(env_path)
        if names:
            loaded_paths.append(env_path)
    return loaded_paths


def get_with_retry(
    session: requests.Session,
    url: str,
    *,
    timeout: float,
    retries: int,
) -> requests.Response:
    retry_statuses = {403, 408, 429, 500, 502, 503, 504}
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            if response.status_code in retry_statuses:
                raise requests.HTTPError(f"HTTP {response.status_code}", response=response)
            response.raise_for_status()
            return response
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
            last_error = exc
            if attempt >= retries:
                break
            time.sleep(min(8.0, 1.4 * attempt))
    raise AgenteComprasError(f"Fallo GET {url} tras {retries} intentos: {last_error}")


def first_text(node: BeautifulSoup, selectors: list[str]) -> str | None:
    for selector in selectors:
        element = node.select_one(selector)
        if element:
            text = clean_text(element.get_text(" ", strip=True))
            if text:
                return text
    return None


def find_product_cards(soup: BeautifulSoup) -> list[Any]:
    cards = soup.select("li.item.product.product-item")
    if cards:
        return cards

    fallback: list[Any] = []
    for element in soup.select("ol.products li.product-item, .products-grid .product-item, div.product-item-info"):
        if element.select_one("a.product-item-link[href]"):
            fallback.append(element)
    return fallback


def infer_availability(text: str, price: float | None, stock_text: str | None) -> bool | None:
    stock_normalized = normalize_text(stock_text or "")
    if "stock disponible" in stock_normalized:
        if "no disponible" in stock_normalized:
            return False
        quantity = extract_stock_quantity(stock_text)
        return quantity is None or quantity > 0
    if "consulta disponibilidad" in stock_normalized or "cotizar aqui" in stock_normalized:
        return False
    if "no disponible" in stock_normalized:
        return False

    normalized = normalize_text(text)
    if "consulta disponibilidad" in normalized and price is None:
        return False
    if "agregar al carro" in normalized or price is not None:
        return True
    if "no disponible" in normalized:
        return False
    return None


def extract_stock_quantity(stock_text: str | None) -> int | None:
    if not stock_text:
        return None
    match = re.search(r"stock\s+disponible\s*:?\s*(\d+)", normalize_text(stock_text))
    if not match:
        return None
    return int(match.group(1))


def extract_sku(text: str, card: Any | None = None) -> str | None:
    if card is not None:
        element = card.select_one("[data-product-sku]")
        if element and element.get("data-product-sku"):
            return clean_text(element.get("data-product-sku"))
    match = re.search(r"\bSKU\s+([A-Z0-9._-]+)", text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_brand(text: str, sku: str | None) -> str | None:
    if not sku or " SKU " not in f" {text} ":
        return None
    before = text.split(" SKU ", 1)[0].strip()
    words = before.split()
    if 1 <= len(words) <= 5:
        return before
    return None


def token_set(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9.]+", normalize_text(value))
        if token not in STOPWORDS and len(token) > 1
    }


def detect_family(value: str) -> str:
    text = normalize_text(value)
    if "diferencial" in text:
        return "interruptor_diferencial"
    if "termomagnetico" in text or re.search(r"\bitm\b", text):
        return "interruptor_termomagnetico"
    if "cable" in text or "conductor" in text or "thw" in text or re.search(r"\btw\b", text):
        return "cable"
    if "curva" in text and "pvc" in text:
        return "curva_pvc"
    if "union" in text and "pvc" in text:
        return "union_pvc"
    if "tubo" in text or "tuberia" in text:
        return "tubo_pvc" if "pvc" in text else "tuberia"
    if "luminaria" in text or "foco" in text or "lampara" in text or "led" in text:
        return "luminaria"
    if "tablero" in text:
        return "tablero"
    if "tomacorriente" in text or "toma corriente" in text:
        return "tomacorriente"
    if "interruptor" in text:
        return "interruptor_control"
    if "electrodo" in text and ("cobread" in text or "tierra" in text):
        return "electrodo_tierra"
    if "caja" in text:
        return "caja"
    if "cinta" in text and "aisl" in text:
        return "cinta"
    if "varilla" in text and "tierra" in text:
        return "varilla_tierra"
    if ("conector" in text or "abrazadera" in text) and "tierra" in text:
        return "conector_tierra"
    return "general"


def extract_specs(value: str) -> set[str]:
    text = normalize_text(value)
    specs: set[str] = set()
    for match in re.finditer(r"\b(\d+)\s*x\s*(\d+(?:[.]\d+)?)\s*a\b", text):
        specs.add(f"{match.group(1)}p")
        specs.add(f"{match.group(2)}a")
    for match in re.finditer(r"\b(\d+)\s*x\s*\d+(?:[.]\d+)?\s+(\d+(?:[.]\d+)?)\s*a\b", text):
        specs.add(f"{match.group(1)}p")
        specs.add(f"{match.group(2)}a")
    patterns = [
        (r"\b(\d+(?:[.]\d+)?)\s*mm2\b", "mm2"),
        (r"\b(\d+(?:[.]\d+)?)\s*mm\b", "mm"),
        (r"\b(\d+(?:[.]\d+)?)\s*ma\b", "ma"),
        (r"\b(\d+(?:[.]\d+)?)\s*a\b", "a"),
        (r"\b(\d+(?:[.]\d+)?)\s*w\b", "w"),
        (r"\b(\d+(?:[.]\d+)?)\s*awg\b", "awg"),
        (r"\b(\d+)\s*p\b|\b(\d+)\s*polos?\b", "p"),
        (r"\b(\d+)\s*circuitos?\b", "circuitos"),
    ]
    for pattern, unit in patterns:
        for match in re.finditer(pattern, text):
            number = next(group for group in match.groups() if group)
            specs.add(f"{number}{unit}")
    for match in re.finditer(r'\b(\d+(?:\s+\d+/\d+|/\d+)?)\s*(?:pulg|")\b', text):
        number = re.sub(r"\s+", "_", match.group(1))
        specs.add(f"{number}pulg")
    if "tubo" in text or "tuberia" in text or "pvc" in text:
        for match in re.finditer(r"\b(\d+(?:\s+\d+/\d+|/\d+))\b", text):
            number = re.sub(r"\s+", "_", match.group(1))
            specs.add(f"{number}pulg")
    return specs


def expand_nominal_specs(specs: set[str]) -> set[str]:
    equivalents = {
        "15mm": {"1/2pulg"},
        "20mm": {"1/2pulg"},
        "25mm": {"3/4pulg"},
        "32mm": {"1pulg"},
        "35mm": {"1pulg"},
        "40mm": {"1_1/4pulg"},
        "50mm": {"1_1/2pulg"},
    }
    expanded = set(specs)
    for spec in specs:
        expanded.update(equivalents.get(spec, set()))
    return expanded


def score_candidate(material_name: str, candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_text = " ".join(
        clean_text(candidate.get(key))
        for key in ("nombre", "texto_visible", "sku", "marca")
        if candidate.get(key)
    )
    material_tokens = token_set(material_name)
    candidate_tokens = token_set(candidate_text)
    overlap = material_tokens & candidate_tokens
    required_family = detect_family(material_name)
    candidate_family = detect_family(candidate_text)
    required_specs = extract_specs(material_name)
    candidate_specs = extract_specs(candidate_text)
    spec_overlap = expand_nominal_specs(required_specs) & expand_nominal_specs(candidate_specs)

    score = len(overlap) * 0.35
    if required_family == candidate_family:
        score += 4.0
    elif required_family != "general" and candidate_family != "general":
        score -= 3.0

    score += len(spec_overlap) * 1.25
    if required_specs and candidate_specs and not spec_overlap:
        score -= 0.75
    elif required_specs and not candidate_specs:
        score -= 1.5
    if candidate.get("disponible") is True:
        score += 0.35
    elif candidate.get("disponible") is False:
        score -= 0.35

    wrong_for_cable = {"alicate", "marcador", "solvente", "limpieza", "herramienta"}
    if required_family == "cable" and candidate_tokens & wrong_for_cable:
        score -= 3.5
    if required_family in {"tubo_pvc", "curva_pvc", "union_pvc"} and "pvc" in overlap:
        score += 0.8
    if required_family.startswith("interruptor") and {"interruptor"} & overlap:
        score += 0.8

    return {
        "coincidencia_score": round(score, 3),
        "familia_requerida": required_family,
        "familia_candidato": candidate_family,
        "tokens_coincidentes": sorted(overlap)[:12],
        "especificaciones_requeridas": sorted(required_specs),
        "especificaciones_coincidentes": sorted(spec_overlap),
    }


def extract_candidates_from_html(
    html: str,
    *,
    material_name: str,
    query: str,
    max_candidates: int,
) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()

    for card in find_product_cards(soup):
        link = card.select_one("a.product-item-link[href]")
        if not link:
            continue
        url = urljoin(PROMELSA_BASE_URL, link.get("href", ""))
        name = clean_text(link.get_text(" ", strip=True))
        if not name or not url:
            continue

        visible_text = clean_text(card.get_text(" ", strip=True))
        sku = extract_sku(visible_text, card)
        key = sku or url
        if key in seen:
            continue
        seen.add(key)

        price_text = first_text(card, [".price", ".special-price .price", "[data-price-type] .price"])
        price = parse_price(price_text)
        stock_text = first_text(card, [".stock", ".availability", ".product-item-stock"])
        if not stock_text and "Consulta disponibilidad" in visible_text:
            stock_text = "Consulta disponibilidad"
        available = infer_availability(visible_text, price, stock_text)

        candidate = {
            "opcion": len(candidates) + 1,
            "nombre": name,
            "marca": extract_brand(visible_text, sku),
            "sku": sku,
            "precio_texto": price_text,
            "precio_soles": price,
            "disponible": available,
            "stock_texto": stock_text,
            "stock_cantidad": extract_stock_quantity(stock_text),
            "url": url,
            "texto_visible": visible_text[:700],
            "consulta": query,
        }
        candidate.update(score_candidate(material_name, candidate))
        candidates.append(candidate)
        if len(candidates) >= max_candidates:
            break
    return candidates


def sort_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(candidate: dict[str, Any]) -> tuple[float, int, int, float]:
        price = candidate.get("precio_soles")
        price_value = float(price) if isinstance(price, (int, float)) else 999999999.0
        return (
            -float(candidate.get("coincidencia_score") or 0),
            0 if candidate.get("disponible") is True else 1,
            0 if price is not None else 1,
            price_value,
        )

    ordered = sorted(candidates, key=key)
    for index, candidate in enumerate(ordered, start=1):
        candidate["opcion"] = index
    return ordered


def buscar_candidatos(
    material_name: str,
    *,
    session: requests.Session,
    max_candidates: int,
    timeout: float,
    retries: int,
) -> SearchResult:
    initial_query = sanitize_query(material_name)
    queries = ordered_unique([initial_query] + relaxed_search_queries(material_name))
    attempted: list[str] = []
    all_candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    first_query_with_results: str | None = None

    for query in queries:
        if not query or query in attempted:
            continue
        attempted.append(query)
        url = PROMELSA_SEARCH_URL.format(termino_de_busqueda=quote_plus(query))
        response = get_with_retry(session, url, timeout=timeout, retries=retries)
        candidates = extract_candidates_from_html(
            response.text,
            material_name=material_name,
            query=query,
            max_candidates=max_candidates,
        )
        if candidates:
            first_query_with_results = first_query_with_results or query
        for candidate in candidates:
            key = candidate.get("sku") or candidate.get("url")
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            all_candidates.append(candidate)

        required_specs = extract_specs(material_name)
        strong_candidates = [
            candidate
            for candidate in all_candidates
            if float(candidate.get("coincidencia_score") or 0) >= 4.0
            and (
                not required_specs
                or bool(candidate.get("especificaciones_coincidentes"))
            )
        ]
        if len(strong_candidates) >= max_candidates:
            break

    if all_candidates:
        ordered = sort_candidates(all_candidates)[:max_candidates]
        used_query = ordered[0].get("consulta") or first_query_with_results
        return SearchResult(
            candidatos=ordered,
            consultas_intentadas=attempted,
            consulta_usada=used_query,
            busqueda_relajada=used_query != initial_query,
        )

    return SearchResult(
        candidatos=[],
        consultas_intentadas=attempted,
        consulta_usada=None,
        busqueda_relajada=len(attempted) > 1,
    )


def prompt_gemini(material_name: str, candidatos: list[dict[str, Any]]) -> str:
    payload = {
        "producto_requerido": material_name,
        "restricciones_ingenieria": [
            "Debe pertenecer a la misma familia tecnica y uso electrico.",
            "Preferir equivalente exacto con stock/precio visible.",
            "Si el exacto no existe o no tiene disponibilidad, elegir el inmediato superior en potencia, calibre, corriente, numero de polos o dimension critica.",
            "Nunca elegir una especificacion inferior a la requerida.",
            "Si todos los candidatos cambian la familia tecnica o son inseguros, devolver opcion null y requiere_revision true.",
        ],
        "equivalencias_comerciales": {
            "pvc_sap_electrico": {
                "nota": "Las pulgadas de catalogo son denominaciones comerciales; no las conviertas como diametro fisico exacto.",
                "15 mm": "1/2 pulg",
                "20 mm": "1/2 pulg",
                "25 mm": "3/4 pulg",
                "32 mm": "1 pulg",
                "35 mm": "1 pulg",
                "40 mm": "1 1/4 pulg",
                "50 mm": "1 1/2 pulg",
            }
        },
        "candidatos_promelsa": candidatos,
    }
    return (
        "Actua como especialista senior en instalaciones electricas y compras tecnicas.\n"
        "Selecciona un producto de Promelsa para el material requerido.\n"
        "Responde estrictamente como JSON valido, sin markdown ni explicaciones fuera del JSON.\n"
        "Formato obligatorio:\n"
        "{\n"
        '  "opcion": 1,\n'
        '  "sku": "SKU elegido o null",\n'
        '  "decision": "equivalente_exacto | inmediato_superior | sin_opcion_segura",\n'
        '  "requiere_revision": false,\n'
        '  "justificacion": "razon tecnica breve",\n'
        '  "criterios": ["familia", "especificacion", "stock"]\n'
        "}\n\n"
        f"Datos:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def response_text_from_gemini(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return text
    parts: list[str] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            part_text = getattr(part, "text", None)
            if part_text:
                parts.append(part_text)
    return "\n".join(parts)


def parse_json_object(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise AgenteComprasError("Gemini no devolvio un objeto JSON parseable.")
        value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise AgenteComprasError("La respuesta JSON de Gemini no es un objeto.")
    return value


def gemini_retry_delay_seconds(exc: Exception, attempt: int, fallback: float) -> float:
    text = str(exc)
    retry_match = re.search(r"Please retry in ([0-9.]+)s", text)
    if retry_match:
        return min(90.0, max(1.0, float(retry_match.group(1)) + 2.0))
    seconds_match = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", text)
    if seconds_match:
        return min(90.0, max(1.0, float(seconds_match.group(1)) + 2.0))
    return min(90.0, max(1.0, fallback * attempt))


def decidir_con_gemini(
    material_name: str,
    candidatos: list[dict[str, Any]],
    *,
    model_name: str,
    retries: int,
    backoff: float,
) -> dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise AgenteComprasError("Falta GEMINI_API_KEY para usar --modo auto.")

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            import google.generativeai as genai
    except ImportError as exc:
        raise AgenteComprasError(
            "Falta instalar google-generativeai para usar --modo auto."
        ) from exc

    genai.configure(api_key=api_key)
    generation_config = {"temperature": 0, "response_mime_type": "application/json"}
    model = genai.GenerativeModel(model_name, generation_config=generation_config)
    prompt = prompt_gemini(material_name, candidatos)
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = model.generate_content(prompt)
            break
        except Exception as exc:
            last_error = exc
            retryable = "429" in str(exc) or "quota" in str(exc).lower() or "temporarily" in str(exc).lower()
            if not retryable or attempt >= retries:
                raise
            time.sleep(gemini_retry_delay_seconds(exc, attempt, backoff))
    else:
        raise AgenteComprasError(f"Gemini no respondio tras {retries} intentos: {last_error}")

    decision = parse_json_object(response_text_from_gemini(response))
    option = decision.get("opcion")

    if isinstance(option, str) and option.strip().isdigit():
        option = int(option.strip())
        decision["opcion"] = option

    if option is None:
        decision.setdefault("decision", "sin_opcion_segura")
        decision.setdefault("requiere_revision", True)
        return decision

    if not isinstance(option, int) or not 1 <= option <= len(candidatos):
        raise AgenteComprasError(
            f"Gemini devolvio una opcion invalida: {decision.get('opcion')!r}."
        )

    decision.setdefault("requiere_revision", False)
    decision["candidato"] = candidatos[option - 1]
    return decision


def render_cli_candidates(material_name: str, candidatos: list[dict[str, Any]], formato: str) -> None:
    if formato == "json":
        payload = {
            "material_requerido": material_name,
            "criterio": (
                "Elige el equivalente exacto con stock/precio; si no existe, "
                "elige el inmediato superior tecnico. Usa 0 para omitir."
            ),
            "candidatos": candidatos,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2), flush=True)
        return

    print(f"\nMaterial requerido: {material_name}", flush=True)
    for candidate in candidatos:
        price = candidate.get("precio_texto") or "sin precio visible"
        stock = candidate.get("stock_texto") or (
            "disponible" if candidate.get("disponible") else "disponibilidad no clara"
        )
        print(
            f"[{candidate['opcion']}] {candidate['nombre']} - {price} - "
            f"SKU {candidate.get('sku') or 's/d'} - {stock}",
            flush=True,
        )


def interfaz_cli(material_name: str, candidatos: list[dict[str, Any]], *, formato: str) -> dict[str, Any]:
    render_cli_candidates(material_name, candidatos, formato)
    while True:
        raw = input("Selecciona opcion Promelsa [1-5, 0/skip para omitir]: ").strip()
        if raw.lower() in {"0", "s", "skip", "omitir", ""}:
            return {
                "opcion": None,
                "decision": "sin_opcion_segura",
                "requiere_revision": True,
                "justificacion": "Seleccion omitida por operador CLI.",
                "criterios": ["operador"],
            }
        if raw.isdigit():
            option = int(raw)
            if 1 <= option <= len(candidatos):
                return {
                    "opcion": option,
                    "decision": "seleccion_cli",
                    "requiere_revision": False,
                    "justificacion": "Seleccion indicada por operador CLI.",
                    "criterios": ["operador_cli"],
                    "candidato": candidatos[option - 1],
                }
        print("Entrada invalida. Ingresa un numero de la lista o 0 para omitir.", flush=True)


def decidir_heuristico_seguro(material_name: str, candidatos: list[dict[str, Any]]) -> dict[str, Any]:
    """Selecciona automaticamente solo una coincidencia tecnicamente trazable.

    No intenta reemplazar el juicio profesional. Exige familia compatible,
    especificaciones nominales coincidentes cuando la consulta las contiene,
    precio visible y ausencia de una declaracion explicita de falta de stock.
    Si no se cumplen esas condiciones devuelve una no-seleccion revisable.
    """
    if not candidatos:
        return {
            "opcion": None,
            "decision": "sin_opcion_segura",
            "requiere_revision": True,
            "justificacion": "La tienda no devolvio candidatos.",
            "criterios": ["sin_candidatos"],
        }

    candidate = candidatos[0]
    required_family = detect_family(material_name)
    candidate_family = candidate.get("familia_candidato") or detect_family(
        " ".join(str(candidate.get(key) or "") for key in ("nombre", "texto_visible"))
    )
    required_specs = extract_specs(material_name)
    matching_specs = set(candidate.get("especificaciones_coincidentes") or [])
    score = float(candidate.get("coincidencia_score") or 0.0)
    family_ok = required_family == candidate_family and required_family != "general"
    specs_ok = not required_specs or bool(matching_specs)
    price_ok = candidate.get("precio_soles") is not None
    availability_ok = candidate.get("disponible") is not False
    score_ok = score >= 4.0
    required_text = normalize_text(material_name)
    candidate_raw_text = " ".join(str(candidate.get(key) or "") for key in ("nombre", "texto_visible"))
    candidate_text = normalize_text(candidate_raw_text)
    semantic_ok = True
    semantic_reason = "sin_restriccion_adicional"
    if required_family == "luminaria" and ({"emergencia", "autonoma"} & token_set(required_text)):
        semantic_ok = bool({"emergencia", "autonoma"} & token_set(candidate_text))
        semantic_reason = "funcion_emergencia"
    if required_family == "luminaria":
        for essential in ("panel", "poste", "ip66"):
            if essential in token_set(required_text) and essential not in token_set(candidate_text):
                semantic_ok = False
                semantic_reason = f"forma_o_aptitud_{essential}"
        required_watts = [float(spec[:-1]) for spec in required_specs if spec.endswith("w")]
        candidate_specs = extract_specs(candidate_text)
        candidate_watts = [float(spec[:-1]) for spec in candidate_specs if spec.endswith("w")]
        if required_watts and candidate_watts and min(candidate_watts) < min(required_watts) * 0.75:
            semantic_ok = False
            semantic_reason = "potencia_real_o_equivalente_ambigua"
        equivalent_range = re.search(r"(\d+(?:[.,]\d+)?)\s*[-/]\s*(\d+(?:[.,]\d+)?)\s*[wW]", candidate_raw_text)
        if required_watts and equivalent_range and float(equivalent_range.group(1).replace(",", ".")) < min(required_watts) * 0.75:
            semantic_ok = False
            semantic_reason = "potencia_real_o_equivalente_ambigua"

    criteria = [
        f"familia:{required_family}={'OK' if family_ok else 'NO'}",
        f"especificacion={'OK' if specs_ok else 'NO'}",
        f"precio_visible={'OK' if price_ok else 'NO'}",
        f"disponibilidad_no_negativa={'OK' if availability_ok else 'NO'}",
        f"score:{score:.3f}={'OK' if score_ok else 'NO'}",
        f"semantica:{semantic_reason}={'OK' if semantic_ok else 'NO'}",
    ]
    if not all((family_ok, specs_ok, price_ok, availability_ok, score_ok, semantic_ok)):
        return {
            "opcion": None,
            "decision": "sin_opcion_segura",
            "requiere_revision": True,
            "justificacion": "El primer candidato no supera todos los filtros tecnicos deterministicos.",
            "criterios": criteria,
        }

    return {
        "opcion": int(candidate["opcion"]),
        "decision": "coincidencia_heuristica_trazable",
        "requiere_revision": True,
        "justificacion": (
            "Coinciden familia y especificacion nominal; hay precio visible y "
            "no se detecto falta de stock. Requiere validacion humana antes de compra."
        ),
        "criterios": criteria,
        "candidato": candidate,
    }


def parse_attributes_table(soup: BeautifulSoup) -> tuple[dict[str, str], list[str]]:
    attributes: dict[str, str] = {}
    links: list[str] = []
    rows = soup.select(".additional-attributes-wrapper table tr, table.additional-attributes tr")

    for row in rows:
        link_nodes = row.select("a[href]")
        for link in link_nodes:
            href = link.get("href")
            if href:
                links.append(urljoin(PROMELSA_BASE_URL, href))

        header = row.select_one("th")
        cells = row.select("td")
        if header and cells:
            label = clean_text(header.get_text(" ", strip=True))
            value = clean_text(cells[-1].get_text(" ", strip=True))
        elif len(cells) >= 2:
            label = clean_text(cells[0].get_text(" ", strip=True))
            value = clean_text(cells[1].get_text(" ", strip=True))
        else:
            label = clean_text(row.get_text(" ", strip=True))
            value = ""

        if label:
            attributes[label] = value

    return attributes, ordered_unique_raw(links)


def find_pdf_links(soup: BeautifulSoup) -> list[str]:
    links: list[str] = []
    for link in soup.select('a[href]'):
        href = link.get("href", "")
        text = normalize_text(link.get_text(" ", strip=True))
        if ".pdf" in href.lower() or "ficha tecnica" in text:
            links.append(urljoin(PROMELSA_BASE_URL, href))
    return ordered_unique_raw(links)


def raspar_ficha_producto(
    candidato: dict[str, Any],
    *,
    session: requests.Session,
    timeout: float,
    retries: int,
) -> dict[str, Any]:
    url = candidato.get("url")
    if not url:
        raise AgenteComprasError("El candidato elegido no tiene URL de producto.")

    response = get_with_retry(session, url, timeout=timeout, retries=retries)
    soup = BeautifulSoup(response.text, "html.parser")
    title = first_text(soup, ["h1.page-title", ".page-title span", '[itemprop="name"]'])
    product_main = first_text(soup, [".product-info-main"]) or ""
    sku_text = first_text(soup, [".product.attribute.sku", ".sku"]) or product_main
    sku = extract_sku(sku_text) or candidato.get("sku")
    price_text = first_text(
        soup,
        [
            ".product-info-main .price",
            ".price-box .price",
            ".price",
            '[itemprop="price"]',
        ],
    )
    price = parse_price(price_text)
    if price is None:
        meta_price = soup.select_one('meta[itemprop="price"], meta[property="product:price:amount"]')
        if meta_price and meta_price.get("content"):
            price = parse_price(meta_price.get("content"))
            price_text = meta_price.get("content")

    stock_text = first_text(soup, [".product-info-main .stock", ".stock", ".availability"])
    description = first_text(
        soup,
        [
            ".product.attribute.description",
            ".product.attribute.overview",
            "#description",
        ],
    )
    attributes, table_links = parse_attributes_table(soup)
    pdf_links = ordered_unique_raw(table_links + find_pdf_links(soup))
    fabric_match = re.search(r"COD\.\s*FAB\.\s*([A-Z0-9._/-]+)", product_main, re.IGNORECASE)
    fabric_code = (
        attributes.get("Referencia De Fabricante")
        or attributes.get("Referencia de Fabricante")
        or (fabric_match.group(1) if fabric_match else None)
    )
    brand = attributes.get("Marca") or candidato.get("marca")
    available = infer_availability(product_main, price, stock_text)

    technical_parts = [title or "", description or ""]
    technical_parts.extend(f"{key}: {value}" for key, value in attributes.items() if value)

    return {
        "nombre": title or candidato.get("nombre"),
        "sku": sku,
        "codigo_fabricante": fabric_code,
        "marca": brand,
        "precio_texto": price_text or candidato.get("precio_texto"),
        "precio_soles": price if price is not None else candidato.get("precio_soles"),
        "stock_texto": stock_text or candidato.get("stock_texto"),
        "stock_cantidad": extract_stock_quantity(stock_text) or candidato.get("stock_cantidad"),
        "disponible": available if available is not None else candidato.get("disponible"),
        "url": response.url,
        "descripcion": description,
        "atributos": attributes,
        "ficha_tecnica_url": pdf_links[0] if pdf_links else None,
        "ficha_tecnica_urls": pdf_links,
        "texto_tecnico": clean_text(" | ".join(part for part in technical_parts if part))[:1800],
    }


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise AgenteComprasError(f"No existe el archivo de entrada: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AgenteComprasError(f"JSON invalido en {path}: {exc}") from exc
    except OSError as exc:
        raise AgenteComprasError(f"No se pudo leer {path}: {exc}") from exc


def get_by_dotted_path(data: Any, dotted_path: str) -> Any:
    current = data
    for part in dotted_path.split("."):
        if isinstance(current, dict):
            if part not in current:
                raise AgenteComprasError(f"No existe la ruta '{dotted_path}' en el JSON.")
            current = current[part]
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            try:
                current = current[index]
            except IndexError as exc:
                raise AgenteComprasError(f"Indice fuera de rango en ruta '{dotted_path}'.") from exc
        else:
            raise AgenteComprasError(f"La ruta '{dotted_path}' no apunta a una lista valida.")
    return current


def locate_material_items(data: Any, items_path: str | None) -> tuple[list[dict[str, Any]], str]:
    if items_path:
        items = get_by_dotted_path(data, items_path)
        path_label = items_path
    elif isinstance(data, list):
        items = data
        path_label = "$"
    elif isinstance(data, dict):
        for key in LIST_KEYS:
            value = data.get(key)
            if isinstance(value, list):
                items = value
                path_label = key
                break
        else:
            raise AgenteComprasError(
                "No se detecto lista de materiales. Usa --items-path para indicarla."
            )
    else:
        raise AgenteComprasError("El JSON debe ser una lista o un objeto con una lista de materiales.")

    if not isinstance(items, list):
        raise AgenteComprasError(f"La ruta '{path_label}' no contiene una lista.")

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if isinstance(item, dict):
            normalized.append(item)
        else:
            items[index] = {"item": str(item)}
            normalized.append(items[index])
    return normalized, path_label


def get_material_query(item: dict[str, Any], key: str) -> str:
    keys = ordered_unique_raw([key, *QUERY_KEYS])
    for candidate_key in keys:
        value = item.get(candidate_key)
        if value is not None and clean_text(value):
            return clean_text(value)
    raise AgenteComprasError(
        f"El item no tiene nombre util. Llaves revisadas: {', '.join(keys)}."
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_no_result_block(
    material_name: str,
    search_result: SearchResult,
    *,
    modo: str,
    status: str,
    message: str,
) -> dict[str, Any]:
    return {
        "estado": status,
        "fuente": "Promelsa",
        "modo": modo,
        "fecha_consulta": now_iso(),
        "consulta_original": material_name,
        "consulta_usada": search_result.consulta_usada,
        "consultas_intentadas": search_result.consultas_intentadas,
        "busqueda_relajada": search_result.busqueda_relajada,
        "requiere_revision": True,
        "mensaje": message,
        "candidatos": search_result.candidatos,
    }


def update_price_fields(item: dict[str, Any], detail: dict[str, Any]) -> dict[str, Any]:
    price = detail.get("precio_soles")
    if price is None:
        return {"precio_actualizado": False, "motivo": "sin_precio_final"}

    previous_price = item.get("precio_unit_soles")
    item["precio_unit_soles"] = round(float(price), 2)
    quantity = parse_float(item.get("cantidad"))
    if quantity is not None:
        item["costo_soles"] = round(quantity * float(price), 2)

    return {
        "precio_actualizado": True,
        "precio_unit_soles_anterior": previous_price,
        "precio_unit_soles_nuevo": item["precio_unit_soles"],
        "costo_soles_nuevo": item.get("costo_soles"),
    }


def attach_quote(
    item: dict[str, Any],
    *,
    material_name: str,
    search_result: SearchResult,
    decision: dict[str, Any],
    detail: dict[str, Any],
    modo: str,
    update_price: bool,
) -> None:
    price_update = update_price_fields(item, detail) if update_price else {"precio_actualizado": False}
    item["cotizacion_promelsa"] = {
        "estado": "OK",
        "fuente": "Promelsa",
        "modo": modo,
        "fecha_consulta": now_iso(),
        "consulta_original": material_name,
        "consulta_usada": search_result.consulta_usada,
        "consultas_intentadas": search_result.consultas_intentadas,
        "busqueda_relajada": search_result.busqueda_relajada,
        "seleccion": {
            "opcion": decision.get("opcion"),
            "decision": decision.get("decision"),
            "requiere_revision": bool(decision.get("requiere_revision")),
            "justificacion": decision.get("justificacion"),
            "criterios": decision.get("criterios", []),
        },
        "producto": detail,
        "candidatos": search_result.candidatos,
        "actualizacion_precio": price_update,
    }


def process_item(
    item: dict[str, Any],
    *,
    item_index: int,
    total: int,
    args: argparse.Namespace,
    session: requests.Session,
) -> str:
    material_name = get_material_query(item, args.key)
    eprint(f"[{item_index}/{total}] Buscando en Promelsa: {material_name}")

    search_result = buscar_candidatos(
        material_name,
        session=session,
        max_candidates=args.max_candidatos,
        timeout=args.timeout,
        retries=args.reintentos,
    )

    if not search_result.candidatos:
        item["cotizacion_promelsa"] = build_no_result_block(
            material_name,
            search_result,
            modo=args.modo,
            status="NO_ENCONTRADO",
            message="Promelsa no devolvio candidatos ni con busqueda relajada.",
        )
        eprint("  Sin candidatos.")
        return "NO_ENCONTRADO"

    eprint(
        f"  {len(search_result.candidatos)} candidatos; consulta usada: "
        f"{search_result.consulta_usada}"
    )

    if args.modo == "auto":
        decision = decidir_con_gemini(
            material_name,
            search_result.candidatos,
            model_name=args.modelo_gemini,
            retries=args.gemini_reintentos,
            backoff=args.gemini_backoff,
        )
    elif args.modo == "heuristico":
        decision = decidir_heuristico_seguro(material_name, search_result.candidatos)
    else:
        decision = interfaz_cli(material_name, search_result.candidatos, formato=args.formato_cli)

    if decision.get("opcion") is None or not decision.get("candidato"):
        item["cotizacion_promelsa"] = build_no_result_block(
            material_name,
            search_result,
            modo=args.modo,
            status="SIN_SELECCION",
            message=decision.get("justificacion") or "No se selecciono un candidato.",
        )
        item["cotizacion_promelsa"]["seleccion"] = {
            "opcion": None,
            "decision": decision.get("decision"),
            "requiere_revision": bool(decision.get("requiere_revision", True)),
            "justificacion": decision.get("justificacion"),
            "criterios": decision.get("criterios", []),
        }
        eprint("  Seleccion omitida.")
        return "SIN_SELECCION"

    detail = raspar_ficha_producto(
        decision["candidato"],
        session=session,
        timeout=args.timeout,
        retries=args.reintentos,
    )
    attach_quote(
        item,
        material_name=material_name,
        search_result=search_result,
        decision=decision,
        detail=detail,
        modo=args.modo,
        update_price=not args.no_actualizar_precio,
    )
    eprint(f"  OK: {detail.get('sku') or 'sin SKU'} - {detail.get('precio_texto') or 'sin precio'}")
    return "OK"


def recalculate_summary(data: Any, items: list[dict[str, Any]]) -> None:
    if not isinstance(data, dict):
        return
    costs = [parse_float(item.get("costo_soles")) for item in items]
    numeric_costs = [cost for cost in costs if cost is not None]
    if numeric_costs and isinstance(data.get("resumen"), dict):
        data["resumen"]["costo_referencial_bom_soles"] = round(sum(numeric_costs), 2)
    data["agente_compras"] = {
        "fuente": "Promelsa",
        "ultima_actualizacion": now_iso(),
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        tmp_path.replace(path)
    except OSError as exc:
        raise AgenteComprasError(f"No se pudo escribir {path}: {exc}") from exc


def guardar_resultados(path: Path, data: Any) -> None:
    write_json(path, data)


def validate_args(args: argparse.Namespace) -> None:
    if args.max_candidatos < 1:
        raise AgenteComprasError("--max-candidatos debe ser mayor o igual a 1.")
    if args.limit is not None and args.limit < 1:
        raise AgenteComprasError("--limit debe ser mayor o igual a 1.")
    if args.delay < 0:
        raise AgenteComprasError("--delay no puede ser negativo.")
    if not 1 <= args.workers <= 6:
        raise AgenteComprasError("--workers debe estar entre 1 y 6.")
    if args.timeout <= 0:
        raise AgenteComprasError("--timeout debe ser positivo.")
    if args.reintentos < 1:
        raise AgenteComprasError("--reintentos debe ser mayor o igual a 1.")
    if args.gemini_reintentos < 1:
        raise AgenteComprasError("--gemini-reintentos debe ser mayor o igual a 1.")
    if args.gemini_backoff <= 0:
        raise AgenteComprasError("--gemini-backoff debe ser positivo.")
    if args.modo == "auto" and not os.environ.get("GEMINI_API_KEY"):
        raise AgenteComprasError("Falta GEMINI_API_KEY para usar --modo auto.")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        input_path = Path(args.input).expanduser().resolve()
        output_path = input_path if args.in_place else Path(args.output).expanduser().resolve()
        loaded_env_paths = load_environment(args, input_path)
        validate_args(args)
        data = load_json(input_path)
        items, path_label = locate_material_items(data, args.items_path)
        selected_items = items[: args.limit] if args.limit else items
        stats: dict[str, int] = {}

        if loaded_env_paths:
            eprint(
                "Variables .env cargadas desde: "
                + ", ".join(str(path) for path in loaded_env_paths)
            )
        eprint(
            f"Materiales detectados en '{path_label}': {len(items)}; "
            f"procesando: {len(selected_items)}."
        )
        def process_with_guard(index: int, item: dict[str, Any]) -> str:
            session = create_session()
            try:
                return process_item(
                    item,
                    item_index=index,
                    total=len(selected_items),
                    args=args,
                    session=session,
                )
            except Exception as exc:
                item["cotizacion_promelsa"] = {
                    "estado": "ERROR",
                    "fuente": "Promelsa",
                    "modo": args.modo,
                    "fecha_consulta": now_iso(),
                    "mensaje": str(exc),
                    "requiere_revision": True,
                }
                eprint(f"  ERROR: {exc}")
                return "ERROR"

        indexed_items = list(enumerate(selected_items, start=1))
        if args.workers == 1:
            for index, item in indexed_items:
                status = process_with_guard(index, item)
                stats[status] = stats.get(status, 0) + 1
                if index < len(selected_items) and args.delay:
                    time.sleep(args.delay)
        else:
            eprint(f"Consultas concurrentes: {args.workers} workers independientes.")
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
                futures = {
                    executor.submit(process_with_guard, index, item): index
                    for index, item in indexed_items
                }
                for future in concurrent.futures.as_completed(futures):
                    status = future.result()
                    stats[status] = stats.get(status, 0) + 1

        recalculate_summary(data, items)
        guardar_resultados(output_path, data)
        eprint(f"JSON actualizado: {output_path}")
        eprint("Resumen: " + ", ".join(f"{key}={value}" for key, value in sorted(stats.items())))
        return 0
    except AgenteComprasError as exc:
        eprint(f"[error] {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
