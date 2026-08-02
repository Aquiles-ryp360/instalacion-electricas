#!/usr/bin/env python3
"""Comprueba en un solo paso que el clon puede regenerar Unidad 2."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256(path: Path, *, normalize_newlines: bool = False) -> str:
    digest = hashlib.sha256()
    if normalize_newlines:
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
        return digest.hexdigest()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


REQUIRED_FILES = {
    "proyectos/unidad-2-industrial/fuentes/local/cad/DISTRIBUCION Y CIRCULACION MIGUEL.dxf": {
        "sha256": "7980dda84d5ea40ed85e5458b487edfc219584d8c4b6e62f7fd9442e7443d805",
        "role": "plano CAD original A-01/S-01/M-01",
    },
    "proyectos/unidad-2-industrial/fuentes/local/ubicacion/2026-08-02-captura-catastro-municipal-caracoto.png": {
        "sha256": "347c550640c2ccc537bf8a0b5acc72c7e2e7003ba003102c5370507a32a03dc2",
        "role": "captura catastral contextual",
    },
    "proyectos/unidad-2-industrial/fuentes/local/ubicacion/2026-08-02-captura-google-maps-caracoto.png": {
        "sha256": "800cf5a92936dee69398803cbc942433db9758ac52925ab858f2cf80c2aae532",
        "role": "captura satelital contextual",
    },
    "proyectos/unidad-2-industrial/fuentes/versionadas/identidad/unap_logo.svg": {
        "sha256": "9f15da7b391761fe2fc9eb64ff0f4039e2d96e95b360056b8cb7b1675152bebe",
        "role": "escudo UNAP vectorial fuente",
    },
    "proyectos/unidad-2-industrial/fuentes/versionadas/identidad/unap_logo.pdf": {
        "sha256": "23078802af82a33d9f578ccf24ac5cade9ec0582ae3433e9a9a68cd0779ae5f9",
        "role": "escudo UNAP vectorial listo para LaTeX",
    },
    "proyectos/unidad-2-industrial/presupuesto/datos/promelsa-base-2026-08-02.json": {
        "sha256": "c365b6e090ea3f2cfd380be7d1314f9a92828c2cf2193535485e6bfe865b38a6",
        "role": "evidencia comercial base para compilacion sin red",
        "normalize_newlines": True,
    },
}

PYTHON_MODULES = {
    "yaml": "PyYAML",
    "PIL": "Pillow",
    "ezdxf": "ezdxf",
    "matplotlib": "matplotlib",
    "requests": "requests",
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "rapidfuzz": "rapidfuzz",
    "pypdf": "pypdf",
    "pytest": "pytest",
}


def is_tracked(root: Path, relative: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", relative],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="imprime el informe como JSON")
    parser.add_argument(
        "--solo-fuentes",
        action="store_true",
        help="comprueba archivos y huellas, sin exigir Python/LaTeX",
    )
    args = parser.parse_args()
    root = repository_root()

    files: list[dict[str, object]] = []
    failures: list[str] = []
    for relative, expected in REQUIRED_FILES.items():
        path = root / relative
        exists = path.is_file()
        actual = sha256(
            path,
            normalize_newlines=bool(expected.get("normalize_newlines")),
        ) if exists else None
        valid = actual == expected["sha256"]
        tracked = is_tracked(root, relative) if exists and shutil.which("git") else False
        files.append({
            "path": relative,
            "role": expected["role"],
            "exists": exists,
            "tracked": tracked,
            "sha256_ok": valid,
            "bytes": path.stat().st_size if exists else 0,
        })
        if not exists or not valid or not tracked:
            failures.append(f"fuente:{relative}")

    modules: list[dict[str, object]] = []
    commands: list[dict[str, object]] = []
    if not args.solo_fuentes:
        for module, package in PYTHON_MODULES.items():
            available = importlib.util.find_spec(module) is not None
            modules.append({"module": module, "package": package, "available": available})
            if not available:
                failures.append(f"python:{package}")
        for command in ("git", "latexmk", "pdflatex"):
            location = shutil.which(command)
            commands.append({"command": command, "available": bool(location), "path": location})
            if not location:
                failures.append(f"command:{command}")
        for command in ("acad.exe", "accoreconsole.exe", "pdfinfo", "pdfimages", "pdftoppm"):
            location = shutil.which(command)
            commands.append({"command": command, "available": bool(location), "path": location, "optional": True})

    report = {
        "status": "READY" if not failures else "INCOMPLETE",
        "repository": str(root),
        "files": files,
        "python_modules": modules,
        "commands": commands,
        "failures": failures,
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Estado: {report['status']}")
        for item in files:
            state = "OK" if item["exists"] and item["tracked"] and item["sha256_ok"] else "FALTA/INVALIDA"
            print(f"[{state}] {item['path']} ({item['role']})")
        for item in modules:
            print(f"[{'OK' if item['available'] else 'FALTA'}] Python: {item['package']}")
        for item in commands:
            optional = " (opcional)" if item.get("optional") else ""
            print(f"[{'OK' if item['available'] else 'FALTA'}] Comando: {item['command']}{optional}")
        if failures:
            print("Pendientes:", ", ".join(failures))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
