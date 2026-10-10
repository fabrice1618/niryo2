#!/usr/bin/env bash
#
# Création des comptes Linux des équipes du projet fil rouge, avec un mot de
# passe aléatoire par compte.
#
# À lancer en administrateur sur chaque machine concernée : postes Linux de la
# salle D3.10, Raspberry Pi (ISTP), NUC du fab lab (IRUP). Les identifiants sont
# les mêmes partout ; les mots de passe aussi si l'on réutilise le même fichier.
#
# Usage : sudo ./creer_comptes_equipes.sh [options] <jeu>
#
#   <jeu>  inge   les 8 équipes de BACHINGE24 : g1e1 à g1e4, g2e1 à g2e4
#          irup   les 6 équipes de l'IRUP : t1e1, t1e2 (BACHTECH24), r1e1 à r1e4 (B3RNSPP26)
#          ou une liste d'identifiants (g1e1 g1e2 ...)
#
# Options :
#   -f, --fichier FICHIER   fichier des mots de passe, une ligne « identifiant:motdepasse »
#                           (défaut : ./comptes_<jeu>.txt). S'il existe déjà, ses mots de
#                           passe sont réutilisés : on obtient les mêmes sur toutes les machines.
#   -l, --longueur N        longueur des mots de passe générés (défaut : 12)
#   -r, --reinitialiser     génère un nouveau mot de passe, même pour un compte existant
#   -s, --simulation        n'applique rien : affiche ce qui serait fait (sans droits admin)
#   -d, --supprimer         supprime les comptes et leurs dossiers (après confirmation)
#   -h, --aide              affiche cette aide
#
# Le fichier des mots de passe contient des secrets : il est créé en lecture
# seule pour son propriétaire (mode 600). Ne le laissez pas sur les postes des
# étudiants une fois les comptes créés.

set -euo pipefail

LONGUEUR=12
FICHIER=""
REINIT=0
SIMULATION=0
SUPPRIMER=0

# Nom d'équipe affiché (commentaire du compte), sans accent.
declare -A NOMS=(
  [g1e1]="Cuivre"  [g1e2]="Fer"     [g1e3]="Zinc"    [g1e4]="Etain"
  [g2e1]="Argent"  [g2e2]="Nickel"  [g2e3]="Cobalt"  [g2e4]="Titane"
  [t1e1]="Vega"    [t1e2]="Altair"
  [r1e1]="Loire"   [r1e2]="Rhone"   [r1e3]="Seine"   [r1e4]="Garonne"
)

aide() { sed -n '3,/^set -euo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'; }
erreur() { echo "Erreur : $*" >&2; exit 1; }

# --- Lecture des options -----------------------------------------------------
JEU=()
while [ $# -gt 0 ]; do
  case "$1" in
    -f|--fichier)       [ $# -ge 2 ] || erreur "$1 attend un argument"; FICHIER=$2; shift 2 ;;
    -l|--longueur)      [ $# -ge 2 ] || erreur "$1 attend un argument"; LONGUEUR=$2; shift 2 ;;
    -r|--reinitialiser) REINIT=1; shift ;;
    -s|--simulation)    SIMULATION=1; shift ;;
    -d|--supprimer)     SUPPRIMER=1; shift ;;
    -h|--aide)          aide; exit 0 ;;
    -*)                 erreur "option inconnue : $1 (voir --aide)" ;;
    *)                  JEU+=("$1"); shift ;;
  esac
done

[ ${#JEU[@]} -gt 0 ] || { aide >&2; exit 1; }
[[ $LONGUEUR =~ ^[0-9]+$ ]] && [ "$LONGUEUR" -ge 8 ] || erreur "la longueur doit être un nombre d'au moins 8"

# --- Liste des identifiants --------------------------------------------------
case "${JEU[0]}" in
  inge) COMPTES=(g1e1 g1e2 g1e3 g1e4 g2e1 g2e2 g2e3 g2e4); NOM_JEU=inge ;;
  irup) COMPTES=(t1e1 t1e2 r1e1 r1e2 r1e3 r1e4);           NOM_JEU=irup ;;
  *)    COMPTES=("${JEU[@]}");                              NOM_JEU=perso ;;
esac
for c in "${COMPTES[@]}"; do
  [[ $c =~ ^[a-z][a-z0-9_-]{1,30}$ ]] || erreur "identifiant invalide : « $c » (minuscules, chiffres, - et _)"
done
[ -n "$FICHIER" ] || FICHIER="./comptes_${NOM_JEU}.txt"

if [ "$SIMULATION" -eq 0 ] && [ "$(id -u)" -ne 0 ]; then
  erreur "à lancer en administrateur (sudo), ou avec --simulation"
fi

# Exécute une commande, ou l'affiche en simulation.
agir() {
  if [ "$SIMULATION" -eq 1 ]; then echo "  [simulation] $*"; else "$@"; fi
}

# --- Suppression -------------------------------------------------------------
if [ "$SUPPRIMER" -eq 1 ]; then
  echo "Comptes à supprimer, avec leur dossier personnel : ${COMPTES[*]}"
  if [ "$SIMULATION" -eq 0 ]; then
    read -r -p "Taper « oui » pour confirmer : " rep
    [ "$rep" = "oui" ] || erreur "suppression annulée"
  fi
  for c in "${COMPTES[@]}"; do
    if id "$c" >/dev/null 2>&1; then
      agir pkill -KILL -u "$c" 2>/dev/null || true
      agir userdel -r "$c" 2>/dev/null || true
      echo "supprimé  : $c"
    else
      echo "absent    : $c"
    fi
  done
  echo "Pensez à supprimer aussi le fichier des mots de passe : $FICHIER"
  exit 0
fi

# --- Mots de passe : lecture du fichier existant ------------------------------
declare -A MDP
if [ -f "$FICHIER" ]; then
  while IFS=: read -r u p || [ -n "$u" ]; do
    case "$u" in ''|'#'*) continue ;; esac
    MDP[$u]=$p
  done < "$FICHIER"
  echo "Mots de passe lus dans $FICHIER (${#MDP[@]} entrée(s))"
fi

# Mot de passe aléatoire, sans caractères ambigus (I, O, l, o, 0, 1).
generer_mdp() {
  local jeu='ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789' mdp=''
  while [ "${#mdp}" -lt "$LONGUEUR" ]; do
    mdp+=$(head -c 256 /dev/urandom | LC_ALL=C tr -dc "$jeu")
  done
  printf '%s' "${mdp:0:$LONGUEUR}"
}

# --- Création des comptes ----------------------------------------------------
RESUME=()
for c in "${COMPTES[@]}"; do
  existe=0; id "$c" >/dev/null 2>&1 && existe=1
  mdp=${MDP[$c]:-}

  if [ "$existe" -eq 1 ] && [ -z "$mdp" ] && [ "$REINIT" -eq 0 ]; then
    RESUME+=("$c|(inchangé)|existe déjà, mot de passe inconnu : utiliser --reinitialiser")
    continue
  fi
  if [ -z "$mdp" ] || [ "$REINIT" -eq 1 ]; then
    mdp=$(generer_mdp)
  fi

  if [ "$existe" -eq 0 ]; then
    agir useradd --create-home --shell /bin/bash --comment "Equipe ${NOMS[$c]:-$c}" "$c"
    etat="créé"
  else
    etat="mot de passe appliqué"
  fi
  # Dossier personnel privé : une équipe ne lit pas les fichiers des autres.
  dossier=$(getent passwd "$c" | cut -d: -f6 || true)
  agir chmod 700 "${dossier:-/home/$c}"
  if [ "$SIMULATION" -eq 1 ]; then
    echo "  [simulation] chpasswd pour $c"
  else
    printf '%s:%s\n' "$c" "$mdp" | chpasswd
  fi
  MDP[$c]=$mdp
  RESUME+=("$c|$mdp|$etat")
done

# --- Écriture du fichier des mots de passe (mode 600) -------------------------
if [ "$SIMULATION" -eq 0 ]; then
  ancien_umask=$(umask); umask 077
  tmp=$(mktemp "${FICHIER}.XXXXXX")
  for u in "${!MDP[@]}"; do printf '%s:%s\n' "$u" "${MDP[$u]}"; done | sort > "$tmp"
  chmod 600 "$tmp"
  mv "$tmp" "$FICHIER"
  umask "$ancien_umask"
fi

# --- Récapitulatif ------------------------------------------------------------
echo
printf '%-8s %-16s %s\n' "Compte" "Mot de passe" "Résultat"
printf '%-8s %-16s %s\n' "------" "------------" "--------"
for l in "${RESUME[@]}"; do
  IFS='|' read -r u p e <<< "$l"
  printf '%-8s %-16s %s\n' "$u" "$p" "$e"
done
echo
if [ "$SIMULATION" -eq 1 ]; then
  echo "Simulation : aucun compte créé, aucun fichier écrit."
else
  echo "Mots de passe enregistrés dans $FICHIER (lecture réservée à son propriétaire)."
  echo "Pour obtenir les mêmes mots de passe sur une autre machine :"
  echo "  sudo $0 --fichier $FICHIER ${JEU[*]}"
fi
