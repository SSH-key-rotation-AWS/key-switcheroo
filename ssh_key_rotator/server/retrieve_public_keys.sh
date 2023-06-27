#!/usr/bin/bash

source "/home/yginsburg/camp-comp-sci/team-henrique/.venv/bin/activate"
echo $(python3.11 /home/yginsburg/camp-comp-sci/team-henrique/ssh_key_rotator/server/retrieve_public_keys.py $1 $2 $3)