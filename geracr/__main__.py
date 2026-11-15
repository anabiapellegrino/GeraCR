#único try do programa
import json
import re
import sys
import xml.etree.ElementTree as ET

from geracr.cli import avisar, executar

try:
    sys.exit(executar(sys.argv[1:]))
except re.error as erro:
    sys.exit(avisar(f"config inválido:\n  - padrão inválido em 'ignorar_na_mensagem': {erro}"))
except (ET.ParseError, json.JSONDecodeError, UnicodeDecodeError, OSError) as erro:
    sys.exit(avisar(f"não consegui ler o arquivo: {erro}"))
