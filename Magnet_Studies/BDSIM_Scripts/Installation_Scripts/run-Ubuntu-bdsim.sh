##set +x

## for mac, must run once
#defaults write org.xquartz.X11 enable_iglx -bool true
## (restart xquartz)

## maybe required to run this to allow incoming network connections
#xhost +
## this works on mac / unix - adapt for windows
#DV=`ipconfig getifaddr en0`
## for windows, the command would roughly be:
## ifconfig /all

## the docker command should have -v <host_dir_abs_path>:<container_dir_abs_path>
## for unix we use `pwd` as a shortcut
#docker run -t -i -v `pwd`:/hostfs -e DISPLAY=$DV:0 --rm bdsim bash

#!/bin/bash

# for mac, must run once
defaults write org.xquartz.X11 enable_iglx -bool true
# (restart xquartz)

# maybe required to run this to allow incoming network connections
xhost +
# this works on mac / unix - adapt for windows
DV=$(ipconfig getifaddr en0)
# for windows, the command would roughly be:
# ifconfig /all

# the docker command should have -v <host_dir_abs_path>:<container_dir_abs_path>
# for unix we use `pwd` as a shortcut
docker run -t -i -v "$(pwd)":/hostfs -e DISPLAY="$DV:0" --rm ubuntu20-bdsim:latest bash
#docker run -t -i -v "$(pwd)":/hostfs -e DISPLAY=host.docker.internal:0 --rm ubuntu20-bdsim:latest bash
#docker run -t -i -v "$(pwd)":/hostfs -e DISPLAY="$DV:0" --net=host --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --rm ubuntu20-bdsim:latest bash
