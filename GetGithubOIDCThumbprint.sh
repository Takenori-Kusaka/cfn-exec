#!/bin/bash

(jwks_uri=$(curl -sL https://token.actions.githubusercontent.com/.well-known/openid-configuration \
    | jq -r '.jwks_uri | split("/")[2]') && \
  echo | openssl s_client -servername $jwks_uri -showcerts -connect $jwks_uri:443 2> /dev/null \
  | openssl x509 -fingerprint -noout \
  | sed -e "s/.*=//" -e "s/://g" \
  | tr "ABCDEF" "abcdef")
