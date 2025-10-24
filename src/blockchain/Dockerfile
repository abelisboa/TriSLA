FROM ubuntu:22.04
WORKDIR /chaincode
COPY entrypoint.sh /chaincode/entrypoint.sh
RUN chmod +x /chaincode/entrypoint.sh
EXPOSE 7051
CMD ["/chaincode/entrypoint.sh"]
