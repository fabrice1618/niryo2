#!/bin/bash
# Lance un programme Python du projet sur le robot Ned2, avec :
#  - les bibliothèques installées par install.sh (~/cellule/libs) ;
#  - l'environnement ROS du robot (Python ROS Wrapper), s'il n'est pas déjà chargé.
# Usage : ~/cellule/lancer.sh app.py [arguments]

LIBS="$HOME/cellule/libs"

if ! python3 -c "import rospy" 2>/dev/null; then
    for f in "$HOME/catkin_ws/install/release/ned2/setup.bash" "$HOME/catkin_ws/devel/setup.bash"; do
        if [ -f "$f" ]; then
            source "$f"
            break
        fi
    done
fi

export PYTHONPATH="$LIBS${PYTHONPATH:+:$PYTHONPATH}"
exec python3 "$@"
