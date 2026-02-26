#!/bin/bash
ssh -o ProxyCommand="ssh -W %h:%p porvir5g@ppgca.unisinos.br" \
    -L 6443:127.0.0.1:6443 \
    porvir5g@node006
