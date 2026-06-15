# Ambiente Experimental

## Cluster

```
Client Version: v1.34.2
Kustomize Version: v5.7.1
Server Version: v1.31.1
Warning: version difference between client (1.34) and server (1.31) exceeds the supported minor version skew of +/-1
```

## Nodes

```
NAME    STATUS   ROLES           AGE    VERSION   INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
node1   Ready    <none>          24d    v1.31.1   192.168.10.16   <none>        Ubuntu 24.04.2 LTS   6.8.0-62-generic    containerd://2.0.3
node2   Ready    control-plane   549d   v1.31.1   192.168.10.15   <none>        Ubuntu 20.04.6 LTS   5.4.0-198-generic   containerd://1.7.23
```

## Namespace (core 5GC)

`ns-1274485`

## Runtime no host de ensaio RAN

- Kubernetes: containerd (nos nós acima).
- Comando local do utilizador: `docker` como alias a Podman (mensagem "Emulate Docker CLI using podman" em corridas documentadas).

Snapshots brutos: `K8S_VERSION.txt`, `K8S_NODES.txt`, `CORE_PODS.txt`.
