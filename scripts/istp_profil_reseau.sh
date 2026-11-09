#!/bin/bash
# NUC d'ISTP : change de profil réseau (fablab, salle ou dhcp).
# Installé dans /usr/local/sbin/profil-reseau par istp_reseau.sh.
# Usage : sudo profil-reseau fablab|salle|dhcp
set -e
profil="cellule-$1"
nmcli -g NAME connection show | grep -qx "$profil" || { echo "Profils : fablab salle dhcp"; exit 1; }
# Au prochain démarrage du NUC, seul le profil choisi démarre
nmcli -g NAME,TYPE connection show | awk -F: '$2=="802-3-ethernet" {print $1}' | while read -r c; do
    nmcli connection modify "$c" connection.autoconnect no
done
nmcli connection modify "$profil" connection.autoconnect yes
nmcli connection up "$profil"
# Serveur DHCP : démarré seulement dans le profil salle
if [ "$1" = salle ]; then
    systemctl enable dnsmasq
    systemctl restart dnsmasq
else
    systemctl disable --now dnsmasq
fi
ip -4 -br addr show scope global
echo "dnsmasq : $(systemctl is-active dnsmasq)"
