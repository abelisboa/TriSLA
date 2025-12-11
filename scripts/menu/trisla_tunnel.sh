ssh -o ProxyCommand="ssh -W %h:%p porvir5g@ppgca.unisinos.br" \
    -L 3000:localhost:3000 \
    -L 9090:localhost:9090 \
    -L 3100:localhost:3100 \
    -L 8088:localhost:8088 \
    node006
