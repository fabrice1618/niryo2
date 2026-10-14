#!/bin/bash
# Installe hors ligne les bibliothèques Python du projet sur le robot Ned2.
# Usage, sur le robot, dans le dossier copié : ./install.sh [options de test.py]
# Exemple : ./install.sh --broker 192.168.1.10
set -e

DOSSIER="$(cd "$(dirname "$0")" && pwd)"
CELLULE="$HOME/cellule"
LIBS="$CELLULE/libs"

echo "== 1. Vérifications"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || {
    echo "Python $(python3 -V 2>&1 | cut -d' ' -f2) : il faut Python 3.8 ou plus (logiciel du robot 5.3 ou plus)."
    exit 1
}
echo "Python $(python3 -V 2>&1 | cut -d' ' -f2), architecture $(uname -m)"
python3 -m pip --version >/dev/null 2>&1 || {
    echo "pip est absent : il faut le paquet python3-pip."
    exit 1
}

echo "== 2. Installation dans $LIBS"
mkdir -p "$LIBS"
python3 -m pip install --no-index --find-links "$DOSSIER/paquets" \
    --target "$LIBS" --upgrade -r "$DOSSIER/requirements.txt"

echo "== 3. Copie du lanceur et du test dans $CELLULE"
install -m 755 "$DOSSIER/lancer.sh" "$CELLULE/lancer.sh"
install -m 644 "$DOSSIER/test.py" "$CELLULE/test.py"

echo "== 4. Test"
if "$CELLULE/lancer.sh" "$CELLULE/test.py" "$@"; then
    echo "Installation terminée. Lancer un programme : ~/cellule/lancer.sh mon_programme.py"
else
    echo "Installation faite, mais au moins un test échoue : voir ci-dessus."
    exit 1
fi
