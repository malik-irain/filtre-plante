FROM nodered/node-red:3.1-debian
USER root
# Installing dependancies
RUN apt-get update
RUN apt-get -y install apt-utils python3-pip sudo
RUN pip3 install spidev smbus automationhat
# We need a user that has root access (and passwordless) in order to execute
# python scripts related to the module
RUN echo '%sudo ALL=(ALL:ALL) NOPASSWD: /usr/bin/python3' | EDITOR='tee -a' visudo
RUN adduser node-red sudo
USER node-red
RUN npm install node-red-contrib-automation-hat
RUN chmod +x /usr/src/node-red/node_modules/node-red-contrib-automation-hat/library/automationhatlink
