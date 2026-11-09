#!/bin/bash
# NUC d'ISTP : prépare le réseau.
#   - crée les trois profils réseau : cellule-fablab, cellule-salle, cellule-dhcp ;
#   - installe la commande « profil-reseau » ;
#   - écrit la configuration du serveur DHCP de la salle (dnsmasq, DHCP seul).
# Ne change pas de profil : ensuite, lancer « sudo profil-reseau fablab|salle|dhcp ».
# Peut être relancé : un profil qui existe déjà n'est pas recréé.
#
# Usage : sudo ./istp_reseau.sh
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }
dossier=$(dirname "$(readlink -f "$0")")

# Nom de l'interface Ethernet du NUC (par exemple enp3s0)
IFACE=$(ip -br link | awk '$1 ~ /^e/ {print $1; exit}')
[ -n "$IFACE" ] || { echo "Aucune interface Ethernet trouvée."; exit 1; }
echo "Interface Ethernet : $IFACE"

ajouter_profil() {   # ajouter_profil <nom> <options nmcli...>
    nom="cellule-$1"; shift
    if nmcli -g NAME connection show | grep -qx "$nom"; then
        echo "Profil $nom : déjà présent"
    else
        nmcli connection add type ethernet ifname "$IFACE" con-name "$nom" autoconnect no "$@"
    fi
}

# Fab lab : adresse fixe, routeur du fab lab
ajouter_profil fablab ipv4.method manual ipv4.addresses 192.168.1.2/24 \
    ipv4.gateway 192.168.1.1 ipv4.dns 192.168.1.1
# Salle D3.10 : même adresse, sans routeur (le NUC y est le serveur DHCP)
ajouter_profil salle ipv4.method manual ipv4.addresses 192.168.1.2/24
# Préparation à la maison ou en cas de doute : adresse donnée par la box
ajouter_profil dhcp ipv4.method auto

# La commande qui change de profil
install -m 755 "$dossier/istp_profil_reseau.sh" /usr/local/sbin/profil-reseau

# Serveur DHCP de la salle : DHCP seul (port=0 désactive le DNS, le port 53 est pris
# par systemd-resolved). Ni passerelle ni DNS envoyés aux postes : la salle n'a pas
# forcément d'accès à Internet. S'il y a un routeur, remplacer les deux dernières
# lignes par dhcp-option=option:router,192.168.1.1 et dhcp-option=option:dns-server,192.168.1.1
cat > /etc/dnsmasq.d/cellule.conf <<CONF
port=0
interface=$IFACE
bind-dynamic
dhcp-authoritative
dhcp-range=192.168.1.100,192.168.1.199,255.255.255.0,12h
dhcp-option=3
dhcp-option=6
CONF
dnsmasq --test

echo
nmcli connection show
echo "Terminé. Changer de profil : sudo profil-reseau fablab|salle|dhcp"
