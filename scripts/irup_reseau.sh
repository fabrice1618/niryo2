#!/bin/bash
# NUC de l'IRUP : adresse IP fixe 192.168.1.2/24 (netplan), routeur 192.168.1.1.
# Avec l'argument « dhcp » : adresse donnée par la box (préparation hors du fab lab).
# Le réseau est reconfiguré tout de suite : une connexion SSH est coupée si l'adresse change.
#
# Usage : sudo ./irup_reseau.sh [dhcp]
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }

# Nom de l'interface Ethernet du NUC (par exemple enp86s0)
IFACE=$(ip -br link | awk '$1 ~ /^e/ {print $1; exit}')
[ -n "$IFACE" ] || { echo "Aucune interface Ethernet trouvée."; exit 1; }
echo "Interface Ethernet : $IFACE"

# cloud-init ne doit plus écraser la configuration réseau
echo "network: {config: disabled}" > /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
rm -f /etc/netplan/*.yaml

if [ "${1:-}" = dhcp ]; then
    cat > /etc/netplan/50-cellule.yaml <<CONF
network:
  version: 2
  ethernets:
    $IFACE:
      dhcp4: true
CONF
else
    cat > /etc/netplan/50-cellule.yaml <<CONF
network:
  version: 2
  ethernets:
    $IFACE:
      dhcp4: false
      addresses: [192.168.1.2/24]
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses: [192.168.1.1]
CONF
fi
chmod 600 /etc/netplan/50-cellule.yaml
netplan apply
ip -4 -br addr show scope global
