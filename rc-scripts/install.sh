#!/bin/sh
install -o root -g wheel -m 0755 init.d/ams-unemployee /etc/init.d && \
install -o root -g wheel -m 0755 conf.d/ams-unemployee /etc/conf.d
