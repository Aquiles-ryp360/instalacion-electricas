"""Crea un paquete corregido de revisión a partir del PDF Rev. 0 comprobado.

La revisión 0A corrige la integridad del ZIP; no modifica el diseño ni el PDF.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from zipfile import ZIP_DEFLATED, ZipFile

from compilar_expediente import BUILD, CHAPTERS, MANIFEST, PDF, ROOT, digest, package_files


ARCHIVE = BUILD / "PAQUETE_REVISION_CAPACHICA_LLACHON_REV0A.zip"
REPORT = BUILD / "MANIFIESTO_PAQUETE_REV0A.json"


def main() -> None:
    if ARCHIVE.exists() or REPORT.exists():
        raise FileExistsError("La revisión 0A ya existe; no se sobrescribe")
    if not PDF.is_file() or not MANIFEST.is_file():
        raise FileNotFoundError("Se necesita el PDF Rev. 0 y su manifiesto original")
    original = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if digest(PDF) != original["pdf_sha256"]:
        raise ValueError("El PDF Rev. 0 no coincide con su manifiesto")
    if {path.name: digest(path) for path in CHAPTERS} != original["source_chapters"]:
        raise ValueError("Los capítulos cambiaron: recompilar el PDF con otra revisión")

    files = package_files()
    file_hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path) for path in files}
    with ZipFile(ARCHIVE, "x", compression=ZIP_DEFLATED) as bundle:
        bundle.write(PDF, arcname=PDF.name)
        for path in files:
            bundle.write(path, arcname=str(path.relative_to(ROOT)).replace("\\", "/"))

    with ZipFile(ARCHIVE) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("ZIP Rev. 0A dañado")
        expected = {PDF.name, *file_hashes}
        if set(bundle.namelist()) != expected:
            raise ValueError("Inventario del ZIP Rev. 0A incompleto")
        for name, sha in file_hashes.items():
            import hashlib
            if hashlib.sha256(bundle.read(name)).hexdigest() != sha:
                raise ValueError(f"Contenido inconsistente: {name}")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "revision": "0A",
        "scope": "Corrección de integridad del paquete; PDF y diseño conservan Rev. 0",
        "status": "DRAFT_FOR_REVIEW_NOT_FOR_CONSTRUCTION",
        "pdf_file": PDF.name,
        "pdf_sha256": digest(PDF),
        "zip_sha256": digest(ARCHIVE),
        "included_files_sha256": file_hashes,
    }
    with REPORT.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(f"ZIP Rev. 0A: {ARCHIVE} ({len(files) + 1} archivos)")


if __name__ == "__main__":
    main()
