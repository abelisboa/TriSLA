FROM hyperledger/besu:23.10.1

COPY genesis.json /opt/besu/genesis.json

ENTRYPOINT ["besu"]

CMD ["--network-id=1337","--data-path=/opt/besu/data","--genesis-file=/opt/besu/genesis.json","--rpc-http-enabled=true","--rpc-http-host=0.0.0.0","--rpc-http-port=8545","--rpc-http-api=ETH,NET,WEB3,ADMIN,DEBUG","--rpc-ws-enabled=true","--rpc-ws-host=0.0.0.0","--rpc-ws-port=8546","--sync-mode=FULL","--logging=INFO"]
