#!/bin/bash
# Pour l'enseignant : retélécharge le dossier paquets/ depuis un poste relié à Internet.
# Le robot Ned2 est un Raspberry Pi 4 (ARM 64 bits, aarch64) ; les paquets couvrent Python 3.8 à 3.12.
set -e

DOSSIER="$(cd "$(dirname "$0")" && pwd)"
PAQUETS="$DOSSIER/paquets"
rm -rf "$PAQUETS"
mkdir -p "$PAQUETS"

# Paquets du fichier requirements.txt, pour chaque version de Python
for v in 3.8 3.9 3.10 3.11 3.12; do
    pip3 download -q --dest "$PAQUETS" --only-binary=:all: --platform manylinux2014_aarch64 \
        --python-version "$v" --implementation cp -r "$DOSSIER/requirements.txt"
done

# Dépendances propres à Python 3.8 et 3.9 (pip les ignore quand le poste a un Python plus récent)
pip3 download -q --dest "$PAQUETS" --only-binary=:all: --platform any --python-version 3.8 \
    --implementation py --no-deps importlib-metadata==8.5.0 zipp==3.20.2

# Secours si le robot n'est pas en aarch64 : MarkupSafe en sources, et de quoi le construire
pip3 download -q --dest "$PAQUETS" --no-binary :all: --no-deps markupsafe==2.1.5
pip3 download -q --dest "$PAQUETS" --only-binary=:all: --platform any --python-version 3.8 \
    --implementation py --no-deps setuptools==75.3.0 wheel==0.45.1

ls "$PAQUETS"
