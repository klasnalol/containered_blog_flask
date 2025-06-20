#!/bin/sh
set -e
CERT=/etc/nginx/certs/selfsigned.crt
KEY=/etc/nginx/certs/selfsigned.key
if [ ! -f "$CERT" ] || [ ! -f "$KEY" ]; then
  mkdir -p /etc/nginx/certs
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$KEY" -out "$CERT" \
    -subj "/CN=localhost"
fi
exec nginx -g 'daemon off;'