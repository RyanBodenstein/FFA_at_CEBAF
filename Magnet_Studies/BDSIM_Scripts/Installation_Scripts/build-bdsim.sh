#docker build . -f Dockerfile-centos7-bdsim -t bdsim
# Need following flag for apple silicon
# softwareupdate --install-rosetta
# docker build . -f Dockerfile-centos-bdsim -t bdsim --platform linux/amd64

# unncomment as appropriate
# first one for host architecture x86_64
#SUFFIX=""
# second one for host architecture arm64
SUFFIX=" --platform linux/arm64/v8"

#docker build . -f Dockerfile-centos7-bdsim-geant4v10.7.2.3-jai-develop --progress=plain -t centos7-bdsim-geant4v10.7.2.3-jai-develop ${SUFFIX}
#docker build . -f Dockerfile-centos7-bdsim-geant4v10.7.2.3-jai-v1.7.0  -t centos7-bdsim-geant4v10.7.2.3-jai-v1.7.0  ${SUFFIX}

docker build . -f Dockerfile-ubuntu20-bdsim  -t ubuntu20-bdsim  ${SUFFIX}
