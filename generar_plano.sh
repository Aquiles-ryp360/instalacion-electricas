#!/bin/bash

# Generador de Planos CAD 2D - Script Automatizado para Linux
# Ejecuta este script desde la raíz del repositorio

# Salir inmediatamente si algún comando falla
set -e

SCRIPT_DIR="proyecto-casa/07-planos/generator"
VENV_DIR="$SCRIPT_DIR/.venv"
INPUT_FILE="$SCRIPT_DIR/layout_example.json"
OUTPUT_FILE="proyecto-casa/07-planos/IE-01-ubicacion-arquitectura.dxf"

echo "=========================================================="
echo "   Iniciando Generador Automático de Planos CAD 2D"
echo "=========================================================="

# 1. Comprobar si Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado en el sistema." >&2
    exit 1
fi

# 2. Crear entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo "Creando entorno virtual de Python en $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# 3. Activar entorno virtual
echo "Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

# 4. Instalar dependencias necesarias
echo "Asegurando dependencias (ezdxf)..."
pip install --quiet ezdxf

# 5. Ejecutar generador de planos
echo "Ejecutando script de generación..."
python3 "$SCRIPT_DIR/dxf_generator.py" --input "$INPUT_FILE" --output "$OUTPUT_FILE"

echo "=========================================================="
echo "   ¡Plano CAD 2D generado con éxito!"
echo "   Archivo de salida: $OUTPUT_FILE"
echo "   Puedes abrirlo en Linux usando QCAD o LibreCAD:"
echo "      qcad \"$OUTPUT_FILE\""
echo "      librecad \"$OUTPUT_FILE\""
echo "=========================================================="
