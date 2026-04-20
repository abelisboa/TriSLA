## CLUSTER
NAME    STATUS   ROLES           AGE     VERSION   INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
node1   Ready    <none>          5d21h   v1.31.1   192.168.10.16   <none>        Ubuntu 24.04.2 LTS   6.8.0-62-generic    containerd://2.0.3
node2   Ready    control-plane   530d    v1.31.1   192.168.10.15   <none>        Ubuntu 20.04.6 LTS   5.4.0-198-generic   containerd://1.7.23

## PODS (TODOS DOM�NIOS)
NAMESPACE            NAME                                                              READY   STATUS              RESTARTS          AGE     IP               NODE    NOMINATED NODE   READINESS GATES
default              node-debugger-node1-g7z74                                         0/1     Completed           0                 47h     192.168.10.16    node1   <none>           <none>
default              node-debugger-node2-6phv4                                         0/1     Completed           0                 6d3h    192.168.10.15    node2   <none>           <none>
default              node-debugger-node2-7skrt                                         0/1     Error               0                 14h     192.168.10.15    node2   <none>           <none>
default              node-debugger-node2-8jwtj                                         0/1     Completed           0                 6d3h    192.168.10.15    node2   <none>           <none>
default              node-debugger-node2-jg2xj                                         0/1     Completed           0                 6d3h    192.168.10.15    node2   <none>           <none>
default              node-debugger-node2-kw9nz                                         0/1     Completed           0                 6d3h    192.168.10.15    node2   <none>           <none>
default              node-debugger-node2-p6bpt                                         0/1     Completed           0                 6d3h    192.168.10.15    node2   <none>           <none>
default              node-debugger-node2-z8ws5                                         0/1     Completed           0                 47h     192.168.10.15    node2   <none>           <none>
grafana              grafana-5c979d8579-865th                                          1/1     Running             2 (15h ago)       9d      10.233.75.53     node2   <none>           <none>
kube-system          calico-kube-controllers-55d498b656-f8h68                          1/1     Running             6 (15h ago)       9d      10.233.75.54     node2   <none>           <none>
kube-system          calico-node-bj9lf                                                 1/1     Running             2 (15h ago)       6d10h   192.168.10.15    node2   <none>           <none>
kube-system          calico-node-frbxz                                                 1/1     Running             1 (5d21h ago)     5d21h   192.168.10.16    node1   <none>           <none>
kube-system          coredns-5bf8c985bd-cr7pn                                          1/1     Running             0                 5d21h   10.233.102.130   node1   <none>           <none>
kube-system          coredns-5bf8c985bd-s5hmz                                          1/1     Running             3 (15h ago)       111d    10.233.75.63     node2   <none>           <none>
kube-system          dns-autoscaler-5cb4578f5f-pbmrx                                   1/1     Running             2 (15h ago)       9d      10.233.75.59     node2   <none>           <none>
kube-system          kube-apiserver-node1                                              1/1     Running             171 (5d21h ago)   5d21h   192.168.10.16    node1   <none>           <none>
kube-system          kube-apiserver-node2                                              1/1     Running             8501 (15h ago)    530d    192.168.10.15    node2   <none>           <none>
kube-system          kube-controller-manager-node1                                     1/1     Running             194 (15h ago)     5d21h   192.168.10.16    node1   <none>           <none>
kube-system          kube-controller-manager-node2                                     1/1     Running             4270 (15h ago)    530d    192.168.10.15    node2   <none>           <none>
kube-system          kube-multus-ds-4hztm                                              1/1     Running             2 (15h ago)       5d22h   192.168.10.15    node2   <none>           <none>
kube-system          kube-multus-ds-f22tj                                              1/1     Running             3 (5d21h ago)     5d21h   192.168.10.16    node1   <none>           <none>
kube-system          kube-proxy-8qtqw                                                  1/1     Running             2 (15h ago)       6d3h    192.168.10.15    node2   <none>           <none>
kube-system          kube-proxy-bc5cc                                                  1/1     Running             3 (5d21h ago)     5d21h   192.168.10.16    node1   <none>           <none>
kube-system          kube-scheduler-node1                                              1/1     Running             176 (15h ago)     5d21h   192.168.10.16    node1   <none>           <none>
kube-system          kube-scheduler-node2                                              1/1     Running             4338 (15h ago)    530d    192.168.10.15    node2   <none>           <none>
kube-system          metrics-server-587b667b55-g82x5                                   1/1     Running             6 (15h ago)       9d      10.233.75.30     node2   <none>           <none>
kube-system          nfs-storage-nfs-subdir-external-provisioner-9f8d6d557-cn7mn       1/1     Running             9 (15h ago)       9d      10.233.75.43     node2   <none>           <none>
kube-system          node-local-dns-9vq4t                                              1/1     Running             6 (15h ago)       125d    192.168.10.15    node2   <none>           <none>
kube-system          node-local-dns-p4zk2                                              1/1     Running             0                 5d21h   192.168.10.16    node1   <none>           <none>
mariadb-operator     mariadb-operator-855f9bbdfd-s8rpd                                 1/1     Running             5 (15h ago)       9d      10.233.75.31     node2   <none>           <none>
mariadb-operator     mariadb-operator-cert-controller-67f78fc9f4-z8vtl                 1/1     Running             2 (15h ago)       9d      10.233.75.33     node2   <none>           <none>
mariadb-operator     mariadb-operator-webhook-5d8c997f76-lxff5                         1/1     Running             2 (15h ago)       9d      10.233.75.22     node2   <none>           <none>
monitoring           alertmanager-prometheus-kube-prometheus-alertmanager-0            2/2     Running             6 (15h ago)       47d     10.233.75.23     node2   <none>           <none>
monitoring           blackbox-exporter-prometheus-blackbox-exporter-8595c75675-cqm4b   1/1     Running             3 (15h ago)       57d     10.233.75.5      node2   <none>           <none>
monitoring           prometheus-grafana-dbc96c9dd-4tmfc                                3/3     Running             9 (15h ago)       47d     10.233.75.61     node2   <none>           <none>
monitoring           prometheus-kube-prometheus-operator-66c465f84d-kmfc4              1/1     Running             7 (15h ago)       40d     10.233.75.4      node2   <none>           <none>
monitoring           prometheus-kube-state-metrics-85667dcbc-rx5s8                     1/1     Running             10 (15h ago)      47d     10.233.75.56     node2   <none>           <none>
monitoring           prometheus-prometheus-kube-prometheus-prometheus-0                2/2     Running             6 (15h ago)       47d     10.233.75.39     node2   <none>           <none>
monitoring           prometheus-prometheus-node-exporter-hlnpk                         1/1     Running             3 (15h ago)       47d     192.168.10.15    node2   <none>           <none>
monitoring           prometheus-prometheus-node-exporter-zkbc5                         1/1     Running             4 (5d21h ago)     5d21h   192.168.10.16    node1   <none>           <none>
monitoring           trisla-jaeger-7d9cf77d4f-z99zv                                    1/1     Running             3 (15h ago)       39d     10.233.75.51     node2   <none>           <none>
monitoring           trisla-otel-collector-opentelemetry-collector-5495489866-wkrmq    1/1     Running             9 (15h ago)       39d     10.233.75.11     node2   <none>           <none>
monitoring           trisla-tempo-0                                                    1/1     Running             5 (15h ago)       39d     10.233.75.19     node2   <none>           <none>
nasp-transport       mininet-fase2                                                     1/1     Running             0                 42h     10.233.102.172   node1   <none>           <none>
nasp-transport       onos-fb87c586c-6rp4l                                              1/1     Running             0                 42h     10.233.102.147   node1   <none>           <none>
nonrtric             a1-sim-osc-0                                                      1/1     Running             2 (15h ago)       9d      10.233.75.7      node2   <none>           <none>
nonrtric             a1-sim-osc-1                                                      1/1     Running             3 (15h ago)       111d    10.233.75.26     node2   <none>           <none>
nonrtric             a1-sim-std-0                                                      1/1     Running             3 (15h ago)       111d    10.233.75.57     node2   <none>           <none>
nonrtric             a1-sim-std-1                                                      1/1     Running             3 (15h ago)       111d    10.233.75.3      node2   <none>           <none>
nonrtric             a1-sim-std2-0                                                     1/1     Running             2 (15h ago)       9d      10.233.75.37     node2   <none>           <none>
nonrtric             a1-sim-std2-1                                                     1/1     Running             2 (15h ago)       9d      10.233.75.50     node2   <none>           <none>
nonrtric             a1controller-7df6dd74c5-tprpr                                     1/1     Running             2 (15h ago)       9d      10.233.75.49     node2   <none>           <none>
nonrtric             capifcore-586c7c5bcf-mw7m2                                        1/1     Running             2 (15h ago)       9d      10.233.75.62     node2   <none>           <none>
nonrtric             controlpanel-5f596b659b-d57zt                                     1/1     Running             2 (15h ago)       9d      10.233.75.1      node2   <none>           <none>
nonrtric             db-7dcc57cd88-65j5x                                               1/1     Running             2 (15h ago)       9d      10.233.75.13     node2   <none>           <none>
nonrtric             dmaapadapterservice-0                                             1/1     Running             2 (15h ago)       9d      10.233.75.15     node2   <none>           <none>
nonrtric             informationservice-0                                              1/1     Running             2 (15h ago)       9d      10.233.75.47     node2   <none>           <none>
nonrtric             nonrtricgateway-7d78c7d5d7-c5t47                                  1/1     Running             2 (15h ago)       9d      10.233.75.28     node2   <none>           <none>
nonrtric             policymanagementservice-0                                         1/1     Running             2 (15h ago)       9d      10.233.75.9      node2   <none>           <none>
nonrtric             rappmanager-0                                                     1/1     Running             4 (15h ago)       9d      10.233.75.58     node2   <none>           <none>
nonrtric             servicemanager-b4898ff6-9s22k                                     1/1     Running             2 (15h ago)       9d      10.233.75.41     node2   <none>           <none>
ns-1274485           amf-free5gc-amf-amf-0                                             1/1     Running             0                 10h     10.233.102.168   node1   <none>           <none>
ns-1274485           ausf-free5gc-ausf-ausf-fdfbdd45d-kg8hg                            1/1     Running             0                 14h     10.233.102.175   node1   <none>           <none>
ns-1274485           curl-udr-prov                                                     0/1     Completed           0                 15h     10.233.102.179   node1   <none>           <none>
ns-1274485           curl-webui                                                        0/1     Completed           0                 4d13h   10.233.102.158   node1   <none>           <none>
ns-1274485           dnn-n6-iperf-peer                                                 1/1     Running             0                 13h     10.233.75.45     node2   <none>           <none>
ns-1274485           mongodb-0                                                         1/1     Running             2 (15h ago)       9d      10.233.75.27     node2   <none>           <none>
ns-1274485           nrf-free5gc-nrf-nrf-79874bb77d-fm9cs                              1/1     Running             0                 14h     10.233.102.146   node1   <none>           <none>
ns-1274485           nssf-free5gc-nssf-nssf-584d7588dd-qwzx4                           1/1     Running             0                 14h     10.233.102.135   node1   <none>           <none>
ns-1274485           pcf-free5gc-pcf-pcf-758685ff58-4dbsc                              1/1     Running             0                 14h     10.233.102.157   node1   <none>           <none>
ns-1274485           rantester-0                                                       1/1     Running             0                 43h     10.233.102.150   node1   <none>           <none>
ns-1274485           smf-free5gc-smf-smf-0                                             1/1     Running             0                 10h     10.233.102.161   node1   <none>           <none>
ns-1274485           udm-free5gc-udm-udm-db6cbb654-78ms7                               1/1     Running             0                 14h     10.233.102.174   node1   <none>           <none>
ns-1274485           udr-free5gc-udr-udr-857b878cb8-z92xn                              1/1     Running             0                 14h     10.233.102.140   node1   <none>           <none>
ns-1274485           upf-free5gc-upf-upf-0                                             1/1     Running             0                 10h     10.233.75.25     node2   <none>           <none>
ns-1274485           webui-free5gc-webui-webui-9f58548bc-fgcst                         1/1     Running             2 (15h ago)       9d      10.233.75.29     node2   <none>           <none>
open5gs              open5gs-upf-b4db79cb9-qngrc                                       0/1     ContainerCreating   0                 9d      <none>           node2   <none>           <none>
ran-test             ran-rantester-grafana-9fc767557-z5t85                             1/1     Running             2 (15h ago)       9d      10.233.75.14     node2   <none>           <none>
srsran               srsenb-5c48fb478d-fdptn                                           1/1     Running             0                 4d16h   10.233.102.177   node1   <none>           <none>
strimzi-system       strimzi-cluster-operator-644596c9b6-74w4l                         1/1     Running             3 (15h ago)       9d      10.233.75.35     node2   <none>           <none>
trisla-multus-test   multus-peer-pod                                                   1/1     Running             46 (28m ago)      46h     10.233.102.187   node1   <none>           <none>
trisla-multus-test   multus-test-pod                                                   1/1     Running             46 (43m ago)      46h     10.233.102.138   node1   <none>           <none>
trisla               besu-genesis-gen                                                  0/1     Completed           0                 71d     <none>           node2   <none>           <none>
trisla               besu-rpc-test                                                     0/1     Completed           0                 71d     <none>           node2   <none>           <none>
trisla               curl-chk                                                          0/1     Completed           0                 72d     <none>           node2   <none>           <none>
trisla               curl-upfmax                                                       0/1     Completed           0                 60d     <none>           node2   <none>           <none>
trisla               curl32                                                            0/1     Completed           0                 2d14h   10.233.102.148   node1   <none>           <none>
trisla               curltest-decision-final                                           0/1     Completed           0                 82d     <none>           node2   <none>           <none>
trisla               curltest-decision4                                                0/1     Completed           0                 82d     <none>           node2   <none>           <none>
trisla               ghcr-pull-test-de                                                 0/1     ImagePullBackOff    0                 14d     10.233.75.21     node2   <none>           <none>
trisla               ghcr-pull-test-sem                                                0/1     ImagePullBackOff    0                 14d     10.233.75.55     node2   <none>           <none>
trisla               ghcr-test                                                         0/1     Unknown             0                 14d     <none>           node2   <none>           <none>
trisla               ghcr-test-de                                                      0/1     Unknown             0                 14d     <none>           node2   <none>           <none>
trisla               http-diag                                                         0/1     Completed           0                 88d     <none>           node2   <none>           <none>
trisla               kafka-6bd4bcdc7b-rdgsm                                            1/1     Running             3 (15h ago)       41d     10.233.75.34     node2   <none>           <none>
trisla               prbpoll1293                                                       0/1     Completed           0                 3d13h   10.233.102.129   node1   <none>           <none>
trisla               prom1293mon                                                       0/1     Completed           0                 3d14h   10.233.102.175   node1   <none>           <none>
trisla               registry-sanity-verify                                            0/1     Completed           0                 111d    <none>           node2   <none>           <none>
trisla               tmp-curl-accept                                                   0/1     Completed           0                 19d     <none>           node2   <none>           <none>
trisla               tmp-shell                                                         1/1     Running             3 (15h ago)       33d     10.233.75.44     node2   <none>           <none>
trisla               trisla-analytics-adapter-86594d5b8f-645pt                         1/1     Running             3 (15h ago)       35d     10.233.75.48     node2   <none>           <none>
trisla               trisla-bc-nssmf-599b574f74-jcj5m                                  1/1     Running             4 (15h ago)       7d10h   10.233.75.36     node2   <none>           <none>
trisla               trisla-besu-756cf5ff69-vjmbg                                      1/1     Running             3 (15h ago)       44d     10.233.75.17     node2   <none>           <none>
trisla               trisla-blockchain-exporter-75776c777f-m7zhp                       1/1     Running             3 (15h ago)       39d     10.233.75.10     node2   <none>           <none>
trisla               trisla-decision-engine-78b689465d-z6jwp                           1/1     Running             0                 21h     10.233.102.178   node1   <none>           <none>
trisla               trisla-decision-engine-trisla-6649f6cc78-pmlq7                    1/1     Running             0                 21h     10.233.102.188   node1   <none>           <none>
trisla               trisla-decision-engine-v1-7d69f8bbf5-qv8hs                        1/1     Running             0                 3d18h   10.233.102.141   node1   <none>           <none>
trisla               trisla-decision-engine-v2-7657ff4c68-lj8xp                        1/1     Running             0                 3d18h   10.233.102.143   node1   <none>           <none>
trisla               trisla-iperf3-client-8gx9k                                        1/1     Running             3 (15h ago)       81d     10.233.75.12     node2   <none>           <none>
trisla               trisla-iperf3-server-76f599c648-58hbh                             1/1     Running             3 (15h ago)       80d     10.233.75.40     node2   <none>           <none>
trisla               trisla-ml-nsmf-64c6c7f96-nkzgf                                    1/1     Running             4 (15h ago)       7d10h   10.233.75.8      node2   <none>           <none>
trisla               trisla-nasp-adapter-6f79f5446b-v4kx4                              1/1     Running             2 (15h ago)       41h     10.233.75.42     node2   <none>           <none>
trisla               trisla-network-exporter-6d8b4d4495-94mn5                          1/1     Running             3 (15h ago)       39d     10.233.75.32     node2   <none>           <none>
trisla               trisla-otel-collector-859cc8466f-jcqff                            1/1     Running             4 (15h ago)       47d     10.233.75.18     node2   <none>           <none>
trisla               trisla-portal-backend-5b6c77fbdb-ks5x7                            1/1     Running             0                 10h     10.233.102.170   node1   <none>           <none>
trisla               trisla-portal-backend-trisla-9f8d89bf9-mpqmz                      1/1     Running             0                 20h     10.233.102.191   node1   <none>           <none>
trisla               trisla-portal-backend-v1-5886d844c7-dfqcx                         1/1     Running             0                 3d18h   10.233.102.132   node1   <none>           <none>
trisla               trisla-portal-backend-v2-5b9466875b-wt45r                         1/1     Running             0                 3d18h   10.233.102.153   node1   <none>           <none>
trisla               trisla-portal-frontend-78ccbcbfdd-kp78v                           1/1     Running             3 (15h ago)       25d     10.233.75.24     node2   <none>           <none>
trisla               trisla-prb-simulator-cf8654758-xj9sj                              1/1     Running             0                 2d11h   10.233.102.156   node1   <none>           <none>
trisla               trisla-ran-ue-upf-proxy-db48f9b54-kmsgr                           1/1     Running             0                 2d11h   10.233.102.152   node1   <none>           <none>
trisla               trisla-sem-csmf-65cb46f8d9-pqzl6                                  1/1     Running             0                 10h     10.233.102.184   node1   <none>           <none>
trisla               trisla-sem-csmf-trisla-78bb86b6fd-s925m                           1/1     Running             1 (15h ago)       21h     10.233.75.16     node2   <none>           <none>
trisla               trisla-sem-csmf-v1-584c8cc86b-8bt8g                               1/1     Running             2 (15h ago)       3d18h   10.233.75.2      node2   <none>           <none>
trisla               trisla-sem-csmf-v2-5d66d7756d-46p9k                               1/1     Running             2 (15h ago)       3d18h   10.233.75.6      node2   <none>           <none>
trisla               trisla-sla-agent-layer-58d6bd5fc7-wngcz                           1/1     Running             4 (15h ago)       7d10h   10.233.75.46     node2   <none>           <none>
trisla               trisla-tempo-bcf9bb868-b4xjl                                      1/1     Running             3 (15h ago)       47d     10.233.75.38     node2   <none>           <none>
trisla               trisla-traffic-exporter-79ff48f977-mr2km                          1/1     Running             3 (15h ago)       32d     10.233.75.52     node2   <none>           <none>
trisla               trisla-ui-dashboard-c9545c94-7f49h                                1/1     Running             0                 5d21h   10.233.102.131   node1   <none>           <none>
ueransim             trisla-gtp-endpoint                                               1/1     Running             0                 16h     10.233.102.166   node1   <none>           <none>
ueransim             ueransim-singlepod-7c48f47d7-xwxh9                                2/2     Running             0                 10h     10.233.75.20     node2   <none>           <none>

## IMAGENS E DIGEST
default node-debugger-node1-g7z74 docker.io/library/busybox:latest docker.io/library/busybox@sha256:1487d0af5f52b4ba31c7e465126ee2123fe3f2305d638e7827681e7cf6c83d5e
default node-debugger-node2-6phv4 docker.io/nicolaka/netshoot:latest docker.io/nicolaka/netshoot@sha256:47b907d662d139d1e2f22bfe14f4efca1e3f1feed283572f47c970c780c03b61
default node-debugger-node2-7skrt docker.io/library/busybox:1.36 docker.io/library/busybox@sha256:355b3a1bf5609da364166913878a8508d4ba30572d02020a97028c75477e24ff
default node-debugger-node2-8jwtj docker.io/nicolaka/netshoot:latest docker.io/nicolaka/netshoot@sha256:47b907d662d139d1e2f22bfe14f4efca1e3f1feed283572f47c970c780c03b61
default node-debugger-node2-jg2xj docker.io/library/busybox:1.36 docker.io/library/busybox@sha256:355b3a1bf5609da364166913878a8508d4ba30572d02020a97028c75477e24ff
default node-debugger-node2-kw9nz docker.io/nicolaka/netshoot:latest docker.io/nicolaka/netshoot@sha256:47b907d662d139d1e2f22bfe14f4efca1e3f1feed283572f47c970c780c03b61
default node-debugger-node2-p6bpt docker.io/library/busybox:1.36 docker.io/library/busybox@sha256:355b3a1bf5609da364166913878a8508d4ba30572d02020a97028c75477e24ff
default node-debugger-node2-z8ws5 docker.io/library/busybox:latest docker.io/library/busybox@sha256:1487d0af5f52b4ba31c7e465126ee2123fe3f2305d638e7827681e7cf6c83d5e
grafana grafana-5c979d8579-865th docker.io/grafana/grafana:11.3.1 docker.io/grafana/grafana@sha256:fa801ab6e1ae035135309580891e09f7eb94d1abdbd2106bdc288030b028158c
kube-system calico-kube-controllers-55d498b656-f8h68 quay.io/calico/kube-controllers:v3.28.1 sha256:9d19dff735fa0889ad6e741790dd1ff35dc4443f14c95bd61459ff0b9162252e
kube-system calico-node-bj9lf quay.io/calico/node:v3.28.1 sha256:8bbeb9e1ee3287b8f750c10383f53fa1ec6f942aaea2a900f666d5e4e63cf4cc
kube-system calico-node-frbxz quay.io/calico/node:v3.28.1 sha256:8bbeb9e1ee3287b8f750c10383f53fa1ec6f942aaea2a900f666d5e4e63cf4cc
kube-system coredns-5bf8c985bd-cr7pn registry.k8s.io/coredns/coredns:v1.11.3 registry.k8s.io/coredns/coredns@sha256:9caabbf6238b189a65d0d6e6ac138de60d6a1c419e5a341fbbb7c78382559c6e
kube-system coredns-5bf8c985bd-s5hmz registry.k8s.io/coredns/coredns:v1.11.3 sha256:c69fa2e9cbf5f42dc48af631e956d3f95724c13f91596bc567591790e5e36db6
kube-system dns-autoscaler-5cb4578f5f-pbmrx registry.k8s.io/cpa/cluster-proportional-autoscaler:v1.8.8 sha256:b6d1a4be0743fd35029afe89eb5d5a0da894d072817575fcf6fddfa94749138b
kube-system kube-apiserver-node1 registry.k8s.io/kube-apiserver:v1.31.1 registry.k8s.io/kube-apiserver@sha256:2409c23dbb5a2b7a81adbb184d3eac43ac653e9b97a7c0ee121b89bb3ef61fdb
kube-system kube-apiserver-node2 registry.k8s.io/kube-apiserver:v1.31.1 registry.k8s.io/kube-apiserver@sha256:2409c23dbb5a2b7a81adbb184d3eac43ac653e9b97a7c0ee121b89bb3ef61fdb
kube-system kube-controller-manager-node1 registry.k8s.io/kube-controller-manager:v1.31.1 registry.k8s.io/kube-controller-manager@sha256:9f9da5b27e03f89599cc40ba89150aebf3b4cff001e6db6d998674b34181e1a1
kube-system kube-controller-manager-node2 registry.k8s.io/kube-controller-manager:v1.31.1 registry.k8s.io/kube-controller-manager@sha256:9f9da5b27e03f89599cc40ba89150aebf3b4cff001e6db6d998674b34181e1a1
kube-system kube-multus-ds-4hztm ghcr.io/k8snetworkplumbingwg/multus-cni:v4.0.2 ghcr.io/k8snetworkplumbingwg/multus-cni@sha256:825aa0a2572184b1475736f95927c52823e00e3db9930f3d41ce0f6e4bacfc49
kube-system kube-multus-ds-f22tj ghcr.io/k8snetworkplumbingwg/multus-cni:v4.0.2 ghcr.io/k8snetworkplumbingwg/multus-cni@sha256:825aa0a2572184b1475736f95927c52823e00e3db9930f3d41ce0f6e4bacfc49
kube-system kube-proxy-8qtqw registry.k8s.io/kube-proxy:v1.31.1 registry.k8s.io/kube-proxy@sha256:4ee50b00484d7f39a90fc4cda92251177ef5ad8fdf2f2a0c768f9e634b4c6d44
kube-system kube-proxy-bc5cc registry.k8s.io/kube-proxy:v1.31.1 registry.k8s.io/kube-proxy@sha256:4ee50b00484d7f39a90fc4cda92251177ef5ad8fdf2f2a0c768f9e634b4c6d44
kube-system kube-scheduler-node1 registry.k8s.io/kube-scheduler:v1.31.1 registry.k8s.io/kube-scheduler@sha256:969a7e96340f3a927b3d652582edec2d6d82a083871d81ef5064b7edaab430d0
kube-system kube-scheduler-node2 registry.k8s.io/kube-scheduler:v1.31.1 registry.k8s.io/kube-scheduler@sha256:969a7e96340f3a927b3d652582edec2d6d82a083871d81ef5064b7edaab430d0
kube-system metrics-server-587b667b55-g82x5 registry.k8s.io/metrics-server/metrics-server:v0.7.2 registry.k8s.io/metrics-server/metrics-server@sha256:ffcb2bf004d6aa0a17d90e0247cf94f2865c8901dcab4427034c341951c239f9
kube-system nfs-storage-nfs-subdir-external-provisioner-9f8d6d557-cn7mn registry.k8s.io/sig-storage/nfs-subdir-external-provisioner:v4.0.2 registry.k8s.io/sig-storage/nfs-subdir-external-provisioner@sha256:63d5e04551ec8b5aae83b6f35938ca5ddc50a88d85492d9731810c31591fa4c9
kube-system node-local-dns-9vq4t registry.k8s.io/dns/k8s-dns-node-cache:1.26.4 registry.k8s.io/dns/k8s-dns-node-cache@sha256:ab52729d7292fbdf764f21daa7b8ba89fd985ac43cec0a13d035a6942d4c1be8
kube-system node-local-dns-p4zk2 registry.k8s.io/dns/k8s-dns-node-cache:1.26.4 registry.k8s.io/dns/k8s-dns-node-cache@sha256:ab52729d7292fbdf764f21daa7b8ba89fd985ac43cec0a13d035a6942d4c1be8
mariadb-operator mariadb-operator-855f9bbdfd-s8rpd docker-registry3.mariadb.com/mariadb-operator/mariadb-operator:0.38.1 docker-registry3.mariadb.com/mariadb-operator/mariadb-operator@sha256:64cede8bb930e4c9a899084583878e4fe883c3fc34456c7dac56886fc30ead38
mariadb-operator mariadb-operator-cert-controller-67f78fc9f4-z8vtl docker-registry3.mariadb.com/mariadb-operator/mariadb-operator:0.38.1 docker-registry3.mariadb.com/mariadb-operator/mariadb-operator@sha256:64cede8bb930e4c9a899084583878e4fe883c3fc34456c7dac56886fc30ead38
mariadb-operator mariadb-operator-webhook-5d8c997f76-lxff5 docker-registry3.mariadb.com/mariadb-operator/mariadb-operator:0.38.1 docker-registry3.mariadb.com/mariadb-operator/mariadb-operator@sha256:64cede8bb930e4c9a899084583878e4fe883c3fc34456c7dac56886fc30ead38
monitoring alertmanager-prometheus-kube-prometheus-alertmanager-0 quay.io/prometheus/alertmanager:v0.28.1 quay.io/prometheus/alertmanager@sha256:27c475db5fb156cab31d5c18a4251ac7ed567746a2483ff264516437a39b15ba
monitoring blackbox-exporter-prometheus-blackbox-exporter-8595c75675-cqm4b quay.io/prometheus/blackbox-exporter:v0.28.0 quay.io/prometheus/blackbox-exporter@sha256:e753ff9f3fc458d02cca5eddab5a77e1c175eee484a8925ac7d524f04366c2fc
monitoring prometheus-grafana-dbc96c9dd-4tmfc docker.io/grafana/grafana:12.3.3 docker.io/grafana/grafana@sha256:9e1e77ade304069aee3196e9a4f210830e96e80ce9a2640891eccc324b152faf
monitoring prometheus-kube-prometheus-operator-66c465f84d-kmfc4 quay.io/prometheus-operator/prometheus-operator:v0.88.1 quay.io/prometheus-operator/prometheus-operator@sha256:d3d65efa3beeacdc9af743fa892daa1e935f23e4de98c84894a4d25d59a840a4
monitoring prometheus-kube-state-metrics-85667dcbc-rx5s8 registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.18.0 registry.k8s.io/kube-state-metrics/kube-state-metrics@sha256:1545919b72e3ae035454fc054131e8d0f14b42ef6fc5b2ad5c751cafa6b2130e
monitoring prometheus-prometheus-kube-prometheus-prometheus-0 quay.io/prometheus-operator/prometheus-config-reloader:v0.88.1 quay.io/prometheus-operator/prometheus-config-reloader@sha256:27da7b23b862e83581872d464a39a9477de705e86e46e3da18cf55d560caaa79
monitoring prometheus-prometheus-node-exporter-hlnpk quay.io/prometheus/node-exporter:v1.10.2 quay.io/prometheus/node-exporter@sha256:337ff1d356b68d39cef853e8c6345de11ce7556bb34cda8bd205bcf2ed30b565
monitoring prometheus-prometheus-node-exporter-zkbc5 quay.io/prometheus/node-exporter:v1.10.2 quay.io/prometheus/node-exporter@sha256:337ff1d356b68d39cef853e8c6345de11ce7556bb34cda8bd205bcf2ed30b565
monitoring trisla-jaeger-7d9cf77d4f-z99zv docker.io/jaegertracing/jaeger:2.15.1 docker.io/jaegertracing/jaeger@sha256:a7dd965687d45507072676db81e6903706ba334dfc92f0c248125cfd9a70c483
monitoring trisla-otel-collector-opentelemetry-collector-5495489866-wkrmq docker.io/otel/opentelemetry-collector-contrib:latest docker.io/otel/opentelemetry-collector-contrib@sha256:e7c92c715f28ff142f3bcaccd4fc5603cf4c71276ef09954a38eb4038500a5a5
monitoring trisla-tempo-0 docker.io/grafana/tempo:2.9.0 docker.io/grafana/tempo@sha256:65a5789759435f1ef696f1953258b9bbdb18eb571d5ce711ff812d2e128288a4
nasp-transport mininet-fase2 docker.io/iwaseyusuke/mininet:latest docker.io/iwaseyusuke/mininet@sha256:1e063a3cc7552212e037290a504120b7acc2bbf4c2b402cf67e05cff0ae21dc1
nasp-transport onos-fb87c586c-6rp4l docker.io/onosproject/onos:2.7.0 docker.io/onosproject/onos@sha256:bc844aaafd64e6b3834c7043bad83fa1eecc6afb6984e9b4887c12e1a307a7c2
nonrtric a1-sim-osc-0 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator:2.8.0 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator@sha256:a59f40876bd611127d7e99bdfb1fb5d0cf42276a5e0cbde3cc32ef736f1733d5
nonrtric a1-sim-osc-1 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator:2.8.0 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator@sha256:a59f40876bd611127d7e99bdfb1fb5d0cf42276a5e0cbde3cc32ef736f1733d5
nonrtric a1-sim-std-0 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator:2.8.0 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator@sha256:a59f40876bd611127d7e99bdfb1fb5d0cf42276a5e0cbde3cc32ef736f1733d5
nonrtric a1-sim-std-1 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator:2.8.0 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator@sha256:a59f40876bd611127d7e99bdfb1fb5d0cf42276a5e0cbde3cc32ef736f1733d5
nonrtric a1-sim-std2-0 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator:2.8.0 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator@sha256:a59f40876bd611127d7e99bdfb1fb5d0cf42276a5e0cbde3cc32ef736f1733d5
nonrtric a1-sim-std2-1 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator:2.8.0 nexus3.o-ran-sc.org:10002/o-ran-sc/a1-simulator@sha256:a59f40876bd611127d7e99bdfb1fb5d0cf42276a5e0cbde3cc32ef736f1733d5
nonrtric a1controller-7df6dd74c5-tprpr nexus3.onap.org:10002/onap/sdnc-image:2.1.6 nexus3.onap.org:10002/onap/sdnc-image@sha256:88bbc05750a7595848c29fec54e9ac27f9a982b8963dfeb4b91986306dabd9c8
nonrtric capifcore-586c7c5bcf-mw7m2 nexus3.o-ran-sc.org:10004/o-ran-sc/nonrtric-plt-capifcore:1.4.0 nexus3.o-ran-sc.org:10004/o-ran-sc/nonrtric-plt-capifcore@sha256:903da6559ab15a969cc48e90b55205961836d26b242b282edfb41882462bedff
nonrtric controlpanel-5f596b659b-d57zt nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-controlpanel:2.5.0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-controlpanel@sha256:645dc6c7543d101be72ee424c869df07475c721bc24a52934cc432fb30cc726f
nonrtric db-7dcc57cd88-65j5x nexus3.o-ran-sc.org:10001/mariadb:10.5 nexus3.o-ran-sc.org:10001/mariadb@sha256:a530aeeefd82f4fa5150f391b6c75462140904780338766f6b03acecb1cca3ce
nonrtric dmaapadapterservice-0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-dmaapadapter:1.4.0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-dmaapadapter@sha256:74845423760696f4b55fb22b256d90d6f368df9231616c418b7079c1fa7d7c46
nonrtric informationservice-0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-informationcoordinatorservice:1.6.0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-informationcoordinatorservice@sha256:2ccf4b6a8fe2dc461605c0953c243c92e6e997e913653053603a6d5144fa9252
nonrtric nonrtricgateway-7d78c7d5d7-c5t47 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-gateway:1.2.0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-gateway@sha256:39372299394d85d065d9ab766c9755657de975f8d2329c942842a0c30d1d20e1
nonrtric policymanagementservice-0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-a1policymanagementservice:2.9.0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-a1policymanagementservice@sha256:b26bed75396fb8e73a10290a3b18ebe23b4d9c8e981f08d791ee8e85bd3b9979
nonrtric rappmanager-0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-rappmanager:0.2.0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-rappmanager@sha256:18aef6239e0a73e67f1d72c2814c600e7a081507c191e1ba6c94ead4ffb7f85f
nonrtric servicemanager-b4898ff6-9s22k nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-servicemanager:0.2.0 nexus3.o-ran-sc.org:10002/o-ran-sc/nonrtric-plt-servicemanager@sha256:d1c38f21ed9b96319af6fa71a9b20c0d57bbc25f0df68e77d41616f931828c6b
ns-1274485 amf-free5gc-amf-amf-0 docker.io/free5gc/amf:v3.4.5 docker.io/free5gc/amf@sha256:cefae185c206fe8be44272dbb3dc6cd15918e305b31f5ab06cbe8b4b0216f71e
ns-1274485 ausf-free5gc-ausf-ausf-fdfbdd45d-kg8hg docker.io/towards5gs/free5gc-ausf:v3.1.1 docker.io/towards5gs/free5gc-ausf@sha256:3a25d67db4498b201d4515fb78cf240adb7d6eb40ae5ff90757575da8d3c669b
ns-1274485 curl-udr-prov docker.io/curlimages/curl:8.5.0 docker.io/curlimages/curl@sha256:08e466006f0860e54fc299378de998935333e0e130a15f6f98482e9f8dab3058
ns-1274485 curl-webui docker.io/curlimages/curl:8.5.0 docker.io/curlimages/curl@sha256:08e466006f0860e54fc299378de998935333e0e130a15f6f98482e9f8dab3058
ns-1274485 dnn-n6-iperf-peer docker.io/nicolaka/netshoot:latest docker.io/nicolaka/netshoot@sha256:47b907d662d139d1e2f22bfe14f4efca1e3f1feed283572f47c970c780c03b61
ns-1274485 mongodb-0 docker.io/bitnami/mongodb:4.4.4-debian-10-r0 docker.io/bitnami/mongodb@sha256:95abfb776bb4e6ee34f7b5b1c811f978d132136035deacdb7143f798f0343a31
ns-1274485 nrf-free5gc-nrf-nrf-79874bb77d-fm9cs docker.io/towards5gs/free5gc-nrf:v3.1.1 docker.io/towards5gs/free5gc-nrf@sha256:847b13ff5fbf9038cfb2144a9d0c0c57af038eb54ac3be2d80866b6e1d8b8715
ns-1274485 nssf-free5gc-nssf-nssf-584d7588dd-qwzx4 docker.io/towards5gs/free5gc-nssf:v3.1.1 docker.io/towards5gs/free5gc-nssf@sha256:899e63110a62237d2b5229d907a13b4217d16feec47d2b89ae69ac75a0265342
ns-1274485 pcf-free5gc-pcf-pcf-758685ff58-4dbsc docker.io/towards5gs/free5gc-pcf:v3.1.1 docker.io/towards5gs/free5gc-pcf@sha256:72462294bae0f2e31b3f54732f42350ce445ad7bda3e47a7e308f57030cefb67
ns-1274485 rantester-0 docker.io/baleeiro17/my5grantester:1.0.1 docker.io/baleeiro17/my5grantester@sha256:ab80922ab9af3befa204b05821284e71b51c8b68a94c7f353fcba642f8ad31f0
ns-1274485 smf-free5gc-smf-smf-0 docker.io/towards5gs/free5gc-smf:v3.1.1 docker.io/towards5gs/free5gc-smf@sha256:fd6525598eb482ebd6dcba657d9c5331c97f3242a4fb39150e94fa811a98b65d
ns-1274485 udm-free5gc-udm-udm-db6cbb654-78ms7 docker.io/towards5gs/free5gc-udm:v3.1.1 docker.io/towards5gs/free5gc-udm@sha256:cc5c6921576842d46b298dce99444ef2ee0f5c777673f94e3d9d6e5db0840493
ns-1274485 udr-free5gc-udr-udr-857b878cb8-z92xn docker.io/towards5gs/free5gc-udr:v3.1.1 docker.io/towards5gs/free5gc-udr@sha256:ccfeb6899be5ba6a0b045fa5fff7d1ef220a66cd79de5f32336f80c20d5119b2
ns-1274485 upf-free5gc-upf-upf-0 docker.io/towards5gs/free5gc-upf:v3.1.1 docker.io/towards5gs/free5gc-upf@sha256:a69f1dc6eec857774959e62e136f68f03c1cf542c07181d2a4a1be3de2c5561f
ns-1274485 webui-free5gc-webui-webui-9f58548bc-fgcst docker.io/towards5gs/free5gc-webui:v3.1.1 docker.io/towards5gs/free5gc-webui@sha256:e60c5be11cddddd4c5d49c7b55b9fbc67c846dd4c25af41b4d5292a7a2aec8f6
open5gs open5gs-upf-b4db79cb9-qngrc open5gs/open5gs:latest 
ran-test ran-rantester-grafana-9fc767557-z5t85 docker.io/grafana/grafana:11.3.0 docker.io/grafana/grafana@sha256:a0f881232a6fb71a0554a47d0fe2203b6888fe77f4cefb7ea62bed7eb54e13c3
srsran srsenb-5c48fb478d-fdptn docker.io/snslab/srsenb:latest docker.io/snslab/srsenb@sha256:a12fa69f0bca1acbaea17adcab6fc5a8e2cceb8cf666afe2b648e31a0e65e668
strimzi-system strimzi-cluster-operator-644596c9b6-74w4l quay.io/strimzi/operator:0.44.0 quay.io/strimzi/operator@sha256:b07b81f7e282dea2e4e29a7c93cfdd911d4715a5c32fe4c4e3d7c71cba3091e8
trisla-multus-test multus-peer-pod docker.io/library/busybox:1.36 docker.io/library/busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662
trisla-multus-test multus-test-pod docker.io/library/busybox:1.36 docker.io/library/busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662
trisla besu-genesis-gen docker.io/hyperledger/besu:latest docker.io/hyperledger/besu@sha256:4ef9e934bb321d916ff245981fd65100dc41446b26b2bed47a2b7d09139a3cbe
trisla besu-rpc-test docker.io/curlimages/curl:8.5.0 docker.io/curlimages/curl@sha256:08e466006f0860e54fc299378de998935333e0e130a15f6f98482e9f8dab3058
trisla curl-chk docker.io/curlimages/curl:latest docker.io/curlimages/curl@sha256:d94d07ba9e7d6de898b6d96c1a072f6f8266c687af78a74f380087a0addf5d17
trisla curl-upfmax docker.io/curlimages/curl:latest docker.io/curlimages/curl@sha256:d94d07ba9e7d6de898b6d96c1a072f6f8266c687af78a74f380087a0addf5d17
trisla curl32 docker.io/curlimages/curl:8.5.0 docker.io/curlimages/curl@sha256:08e466006f0860e54fc299378de998935333e0e130a15f6f98482e9f8dab3058
trisla curltest-decision-final docker.io/curlimages/curl:latest docker.io/curlimages/curl@sha256:d94d07ba9e7d6de898b6d96c1a072f6f8266c687af78a74f380087a0addf5d17
trisla curltest-decision4 docker.io/curlimages/curl:latest docker.io/curlimages/curl@sha256:d94d07ba9e7d6de898b6d96c1a072f6f8266c687af78a74f380087a0addf5d17
trisla ghcr-pull-test-de ghcr.io/abelisboa/trisla-decision-engine@sha256:3d1597c1a910cce917a0e6f0b7fb4ccee2f684249a41b3abc2d3ae9df5f5c682 
trisla ghcr-pull-test-sem ghcr.io/abelisboa/trisla-sem-csmf@sha256:4b2236f744f2853d263c7424a6cea4ebde15ce5626633c0ce14682c5b50c431c 
trisla ghcr-test sha256:4c3f212677c1314e1d780da0cbd9066aed39d936bd1593fcabacd72f3456b1f4 ghcr.io/abelisboa/trisla-sem-csmf@sha256:1c02cef667f89c191d6a784c08c3bf5d8f60dbc1d3b163f307db260331575240
trisla ghcr-test-de sha256:1959b2a2856532ac5a2fe6b3ce98f0c3822bd5107d8b771e3c8abd86f5de831c ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f
trisla http-diag docker.io/curlimages/curl:8.6.0 docker.io/curlimages/curl@sha256:c3b8bee303c6c6beed656cfc921218c529d65aa61114eb9e27c62047a1271b9b
trisla kafka-6bd4bcdc7b-rdgsm ghcr.io/abelisboa/trisla-kafka:v3.11.2 ghcr.io/abelisboa/trisla-kafka@sha256:8291bed273105a3fc88df5f89096abf6a654dc92b0937245dcef85011f3fc5e6
trisla prbpoll1293 docker.io/curlimages/curl:8.5.0 docker.io/curlimages/curl@sha256:08e466006f0860e54fc299378de998935333e0e130a15f6f98482e9f8dab3058
trisla prom1293mon docker.io/curlimages/curl:8.5.0 docker.io/curlimages/curl@sha256:08e466006f0860e54fc299378de998935333e0e130a15f6f98482e9f8dab3058
trisla registry-sanity-verify 192.168.10.16:5000/library/alpine:latest 192.168.10.16:5000/library/alpine@sha256:0464c44011486f1f7f99d3792d048663ce27d85f9cc8f3218fc8f96f070405af
trisla tmp-curl-accept docker.io/curlimages/curl:latest docker.io/curlimages/curl@sha256:d94d07ba9e7d6de898b6d96c1a072f6f8266c687af78a74f380087a0addf5d17
trisla tmp-shell docker.io/library/busybox:latest docker.io/library/busybox@sha256:1487d0af5f52b4ba31c7e465126ee2123fe3f2305d638e7827681e7cf6c83d5e
trisla trisla-analytics-adapter-86594d5b8f-645pt docker.io/library/python:3.11-slim docker.io/library/python@sha256:9e1912aab0a30bbd9488eb79063f68f42a68ab0946cbe98fecf197fe5b085506
trisla trisla-bc-nssmf-599b574f74-jcj5m sha256:d4797f570bd533e033c0765a48f29cc1ede63821d4850de0f687cad9d6bfccc8 ghcr.io/abelisboa/trisla-bc-nssmf@sha256:b0db5eef2128baddee2c1c3ea72fb5fec421afb1d87407e5f4a6aadd75f9f95a
trisla trisla-besu-756cf5ff69-vjmbg docker.io/hyperledger/besu:23.10.1 docker.io/hyperledger/besu@sha256:3fc09eb10360d28970ba27fca7cbfa2091985e921b1ccf49f9974e1501c5347d
trisla trisla-blockchain-exporter-75776c777f-m7zhp sha256:e71d57d09e3c149d4b68afca4b8c4f9c3a698b00422b3eb0edf4857842c62cbb ghcr.io/abelisboa/trisla-blockchain-exporter@sha256:cae3600a15294a41295928d2ec1814561d66ded42d0945d8da10870a5c0e4a3d
trisla trisla-decision-engine-78b689465d-z6jwp sha256:d3b7ef8d3ded8b771fb5b62ca72dc24196913418939611a1cd69cc561756ec2a ghcr.io/abelisboa/trisla-decision-engine@sha256:ae2919354aff9d2a1c95a1a7096f1f3d96403b03bbb3603bab29fae2a643d39c
trisla trisla-decision-engine-trisla-6649f6cc78-pmlq7 sha256:1959b2a2856532ac5a2fe6b3ce98f0c3822bd5107d8b771e3c8abd86f5de831c ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f
trisla trisla-decision-engine-v1-7d69f8bbf5-qv8hs sha256:1959b2a2856532ac5a2fe6b3ce98f0c3822bd5107d8b771e3c8abd86f5de831c ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f
trisla trisla-decision-engine-v2-7657ff4c68-lj8xp sha256:1959b2a2856532ac5a2fe6b3ce98f0c3822bd5107d8b771e3c8abd86f5de831c ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f
trisla trisla-iperf3-client-8gx9k docker.io/networkstatic/iperf3:latest docker.io/networkstatic/iperf3@sha256:07dcca91c0e47d82d83d91de8c3d46b840eef4180499456b4fa8d6dadb46b6c8
trisla trisla-iperf3-server-76f599c648-58hbh docker.io/networkstatic/iperf3:latest docker.io/networkstatic/iperf3@sha256:07dcca91c0e47d82d83d91de8c3d46b840eef4180499456b4fa8d6dadb46b6c8
trisla trisla-ml-nsmf-64c6c7f96-nkzgf sha256:2e02b762078cdc64e07a30ec77798d283dc632c6458a1fa75e031794bf480f4b ghcr.io/abelisboa/trisla-ml-nsmf@sha256:0e6f14940b753626cf5c2057bf6a6a2633c8b0ddc7cc913abaf6253aa40ace3e
trisla trisla-nasp-adapter-6f79f5446b-v4kx4 sha256:aeaa8244b63ddc5983ef79fa6117dc76261ab1c348903da89def7da34dd21ac5 ghcr.io/abelisboa/trisla-nasp-adapter@sha256:063bddea5a6fcb38d8de504f91cc63b9ab13d5369dff43b6742cc5ae3ab02d79
trisla trisla-network-exporter-6d8b4d4495-94mn5 sha256:fa26c48588c5cf4bbccdb61f8dc3c742e33afb868207e1dcbb8237bc9ebafc07 ghcr.io/abelisboa/trisla-network-exporter@sha256:c17d33431ea923120899ff1d9f5b6561183dd07cc392e5ccf0340b2898a5ba95
trisla trisla-otel-collector-859cc8466f-jcqff docker.io/otel/opentelemetry-collector:0.92.0 docker.io/otel/opentelemetry-collector@sha256:92f6e2efd014152bee26f8324e3a511980b512a36d8793d3fee708715caaa6c0
trisla trisla-portal-backend-5b6c77fbdb-ks5x7 sha256:211a553ca59a4fd9458977f7ba7c68559952c08e40d298fdd1cd2415e332257a ghcr.io/abelisboa/trisla-portal-backend@sha256:8435c4b5c6de1e3ccdc7d2b9721af6f360f4adcdc67f954bf64ad027181b1ea7
trisla trisla-portal-backend-trisla-9f8d89bf9-mpqmz sha256:d7468151492a53b9ce5ee27b02c92c23177f9983655879623b276f07b7d08c24 ghcr.io/abelisboa/trisla-portal-backend@sha256:2961a3eb7a90c96673f1789bc93502880f6a8bf47c50afd5fe7a6f0df1cbae7d
trisla trisla-portal-backend-v1-5886d844c7-dfqcx sha256:d7468151492a53b9ce5ee27b02c92c23177f9983655879623b276f07b7d08c24 ghcr.io/abelisboa/trisla-portal-backend@sha256:2961a3eb7a90c96673f1789bc93502880f6a8bf47c50afd5fe7a6f0df1cbae7d
trisla trisla-portal-backend-v2-5b9466875b-wt45r sha256:d7468151492a53b9ce5ee27b02c92c23177f9983655879623b276f07b7d08c24 ghcr.io/abelisboa/trisla-portal-backend@sha256:2961a3eb7a90c96673f1789bc93502880f6a8bf47c50afd5fe7a6f0df1cbae7d
trisla trisla-portal-frontend-78ccbcbfdd-kp78v sha256:a0121da8db70f18aa3f0920ae7481c9ea25326c6ea3a6c79a87d69a49b9d094d ghcr.io/abelisboa/trisla-portal-frontend@sha256:1a1b82fc1e5b97cf1b4617354e5ac709507b5934864aea71fe2e84e8239d4d2f
trisla trisla-prb-simulator-cf8654758-xj9sj docker.io/library/python:3.10-slim docker.io/library/python@sha256:4ba18b066cee17f2696cf9a2ba564d7d5eb05a91d6a949326780aa7c6912160d
trisla trisla-ran-ue-upf-proxy-db48f9b54-kmsgr docker.io/library/python:3.11-slim docker.io/library/python@sha256:233de06753d30d120b1a3ce359d8d3be8bda78524cd8f520c99883bfe33964cf
trisla trisla-sem-csmf-65cb46f8d9-pqzl6 sha256:4f85303dd69fe7807c80e91e242c93d31f2c6c3461d23ef3877eac838b0d58d9 ghcr.io/abelisboa/trisla-sem-csmf@sha256:5e7252a4285b243fe2ac483fb235d393c51141c9970a68cbf1ff8a666b4f3ec3
trisla trisla-sem-csmf-trisla-78bb86b6fd-s925m sha256:54309327c98072b6a6a686f11595202aeec1672a5be5540859a86425b1ee9998 ghcr.io/abelisboa/trisla-sem-csmf@sha256:31f32c78db0c07165c5ac6fa0f2b46af75fcfc5162a214d23ef0bd18f577f541
trisla trisla-sem-csmf-v1-584c8cc86b-8bt8g sha256:54309327c98072b6a6a686f11595202aeec1672a5be5540859a86425b1ee9998 ghcr.io/abelisboa/trisla-sem-csmf@sha256:31f32c78db0c07165c5ac6fa0f2b46af75fcfc5162a214d23ef0bd18f577f541
trisla trisla-sem-csmf-v2-5d66d7756d-46p9k sha256:54309327c98072b6a6a686f11595202aeec1672a5be5540859a86425b1ee9998 ghcr.io/abelisboa/trisla-sem-csmf@sha256:31f32c78db0c07165c5ac6fa0f2b46af75fcfc5162a214d23ef0bd18f577f541
trisla trisla-sla-agent-layer-58d6bd5fc7-wngcz sha256:bafb742dd4c1e1bb169173cc67d0e8a51d65a277da04361403693679ec99fcb0 ghcr.io/abelisboa/trisla-sla-agent-layer@sha256:397fef296ced041745eb9170524a875ac83e1c96e09f0c7248c49d051983f9f3
trisla trisla-tempo-bcf9bb868-b4xjl docker.io/grafana/tempo:2.4.1 docker.io/grafana/tempo@sha256:5b9c08f6d8fb43b3b72dfd1252ba4f198b11a245257bf76ee2ca13e243bac565
trisla trisla-traffic-exporter-79ff48f977-mr2km ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-traffic-exporter:v3.11.2 ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-traffic-exporter@sha256:a39455f913ea4f7355426b48613cc0479c7e549d099bdba520fd4fb563564f48
trisla trisla-ui-dashboard-c9545c94-7f49h ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-ui-dashboard:v3.11.2 ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-ui-dashboard@sha256:16e23f4de91582e56bfe4704c0139a3154c34c4a44780f17f3082b6195dbe6fb
ueransim trisla-gtp-endpoint docker.io/networkstatic/iperf3:latest docker.io/networkstatic/iperf3@sha256:07dcca91c0e47d82d83d91de8c3d46b840eef4180499456b4fa8d6dadb46b6c8
ueransim ueransim-singlepod-7c48f47d7-xwxh9 docker.io/free5gc/ueransim:v4.2.1-x86_64 docker.io/free5gc/ueransim@sha256:21fab7112edb449691545e27dd5781e7897e1dca2448726a27c22ac92c7ea059

## CORE (FREE5GC)
NAME                                        READY   STATUS      RESTARTS      AGE     IP               NODE    NOMINATED NODE   READINESS GATES
amf-free5gc-amf-amf-0                       1/1     Running     0             10h     10.233.102.168   node1   <none>           <none>
ausf-free5gc-ausf-ausf-fdfbdd45d-kg8hg      1/1     Running     0             14h     10.233.102.175   node1   <none>           <none>
curl-udr-prov                               0/1     Completed   0             15h     10.233.102.179   node1   <none>           <none>
curl-webui                                  0/1     Completed   0             4d13h   10.233.102.158   node1   <none>           <none>
dnn-n6-iperf-peer                           1/1     Running     0             13h     10.233.75.45     node2   <none>           <none>
mongodb-0                                   1/1     Running     2 (15h ago)   9d      10.233.75.27     node2   <none>           <none>
nrf-free5gc-nrf-nrf-79874bb77d-fm9cs        1/1     Running     0             14h     10.233.102.146   node1   <none>           <none>
nssf-free5gc-nssf-nssf-584d7588dd-qwzx4     1/1     Running     0             14h     10.233.102.135   node1   <none>           <none>
pcf-free5gc-pcf-pcf-758685ff58-4dbsc        1/1     Running     0             14h     10.233.102.157   node1   <none>           <none>
rantester-0                                 1/1     Running     0             43h     10.233.102.150   node1   <none>           <none>
smf-free5gc-smf-smf-0                       1/1     Running     0             10h     10.233.102.161   node1   <none>           <none>
udm-free5gc-udm-udm-db6cbb654-78ms7         1/1     Running     0             14h     10.233.102.174   node1   <none>           <none>
udr-free5gc-udr-udr-857b878cb8-z92xn        1/1     Running     0             14h     10.233.102.140   node1   <none>           <none>
upf-free5gc-upf-upf-0                       1/1     Running     0             10h     10.233.75.25     node2   <none>           <none>
webui-free5gc-webui-webui-9f58548bc-fgcst   1/1     Running     2 (15h ago)   9d      10.233.75.29     node2   <none>           <none>

### SMF LOGS (EVID?NCIA)
2026-04-13T01:45:11Z[36m [INFO][SMF][CFG] [0mSMF config version [1.0.2]
2026-04-13T01:45:11Z[36m [INFO][SMF][CFG] [0mUE-Routing config version [1.0.1]
2026-04-13T01:45:11Z[36m [INFO][SMF][Init] [0mSMF Log level is set to [info] level
2026-04-13T01:45:11Z[36m [INFO][LIB][NAS] [0mset log level : info
2026-04-13T01:45:11Z[36m [INFO][LIB][NAS] [0mset report call : false
2026-04-13T01:45:11Z[36m [INFO][LIB][NGAP] [0mset log level : info
2026-04-13T01:45:11Z[36m [INFO][LIB][NGAP] [0mset report call : false
2026-04-13T01:45:11Z[36m [INFO][LIB][Aper] [0mset log level : info
2026-04-13T01:45:11Z[36m [INFO][LIB][Aper] [0mset report call : false
2026-04-13T01:45:11Z[36m [INFO][LIB][PFCP] [0mset log level : info
2026-04-13T01:45:11Z[36m [INFO][LIB][PFCP] [0mset report call : false
2026-04-13T01:45:11Z[36m [INFO][SMF][App] [0msmf
2026-04-13T01:45:11Z[36m [INFO][SMF][App] [0mSMF version:  
	free5GC version: v3.1.1
	build time:      2022-04-28T12:50:59Z
	commit hash:     84c979a3
	commit time:     2022-04-09T08:38:26Z
	go version:      go1.14.4 linux/amd64
2026-04-13T01:45:11Z[36m [INFO][SMF][CTX] [0msmfconfig Info: Version[1.0.2] Description[SMF initial local configuration]
2026-04-13T01:45:11Z[36m [INFO][SMF][CTX] [0mEndpoints: [upf-service]
2026-04-13T01:45:11Z[36m [INFO][SMF][Init] [0mServer started
2026-04-13T01:45:11Z[36m [INFO][SMF][Init] [0mSMF Registration to NRF {e6dcf4c3-6c52-44a8-bd96-69c18cb9fd02 SMF REGISTERED 0 0xc0005201e0 0xc000520220 [] []   [smf-nsmf] [] <nil> [] [] <nil> 0 0 0 area1 <nil> <nil> <nil> <nil> 0xc0002403c0 <nil> <nil> <nil> <nil> <nil> map[] <nil> false 0xc000520040 false false []}
2026-04-13T01:45:11Z[36m [INFO][SMF][PFCP] [0mListen on 10.233.102.161:8805
2026-04-13T01:45:11Z[36m [INFO][SMF][App] [0mSend PFCP Association Request to UPF[upf-service](10.233.75.25)
2026-04-13T01:45:11Z[36m [INFO][LIB][PFCP] [0mRemove Request Transaction [1]
2026-04-13T01:45:11Z[36m [INFO][SMF][PFCP] [0mIn HandlePfcpAssociationSetupResponse
2026-04-13T01:45:11Z[36m [INFO][SMF][PFCP] [0mHandle PFCP Association Setup Response with NodeID[10.233.75.25]
2026-04-13T01:45:11Z[36m [INFO][SMF][PFCP] [0mUPF(10.233.75.25)[{internet}] setup association
2026-04-13T01:45:37Z[36m [INFO][SMF][PduSess] [0mReceive Create SM Context Request
2026-04-13T01:45:37Z[36m [INFO][SMF][PduSess] [0mIn HandlePDUSessionSMContextCreate
2026-04-13T01:45:37Z[36m [INFO][SMF][PduSess] [0mSend NF Discovery Serving UDM Successfully
2026-04-13T01:45:37Z[36m [INFO][SMF][CTX] [0mAllocated UE IP address: 10.1.0.1
2026-04-13T01:45:37Z[36m [INFO][SMF][CTX] [0mSelected UPF: UPF
2026-04-13T01:45:37Z[36m [INFO][SMF][PduSess] [0mUE[imsi-208930000000001] PDUSessionID[1] IP[10.1.0.1]
2026-04-13T01:45:37Z[36m [INFO][SMF][GSM] [0mIn HandlePDUSessionEstablishmentRequest
2026-04-13T01:45:37Z[36m [INFO][NAS][Convert] [0mProtocolOrContainerList:  [0xc00040b9c0 0xc00040ba00]
2026-04-13T01:45:37Z[36m [INFO][SMF][GSM] [0mProtocol Configuration Options
2026-04-13T01:45:37Z[36m [INFO][SMF][GSM] [0m&{[0xc00040b9c0 0xc00040ba00]}
2026-04-13T01:45:37Z[36m [INFO][SMF][GSM] [0mDidn't Implement container type IPAddressAllocationViaNASSignallingUL
2026-04-13T01:45:37Z[36m [INFO][SMF][PduSess] [0mPCF Selection for SMContext SUPI[imsi-208930000000001] PDUSessionID[1]
2026-04-13T01:45:37Z[36m [INFO][SMF][PduSess] [0mSUPI[imsi-208930000000001] has no pre-config route
2026-04-13T01:45:37Z[36m [INFO][SMF][Consumer] [0mSendNFDiscoveryServingAMF ok
2026-04-13T01:45:37Z[36m [INFO][SMF][GIN] [0m| 201 |  10.233.102.168 | POST    | /nsmf-pdusession/v1/sm-contexts |
2026-04-13T01:45:37Z[36m [INFO][SMF][PFCP] [0mIn HandlePfcpSessionEstablishmentResponse
2026-04-13T01:45:37Z[36m [INFO][LIB][PFCP] [0mRemove Request Transaction [2]
2026-04-13T01:45:37Z[36m [INFO][SMF][PduSess] [0mReceive Update SM Context Request
2026-04-13T01:45:37Z[36m [INFO][SMF][PduSess] [0mIn HandlePDUSessionSMContextUpdate
2026-04-13T01:45:37Z[36m [INFO][SMF][PFCP] [0mIn HandlePfcpSessionModificationResponse
2026-04-13T01:45:37Z[36m [INFO][SMF][PduSess] [0m[SMF] PFCP Modification Resonse Accept
2026-04-13T01:45:37Z[36m [INFO][LIB][PFCP] [0mRemove Request Transaction [3]
2026-04-13T01:45:37Z[36m [INFO][SMF][PFCP] [0mPFCP Session Modification Success[1]
2026-04-13T01:45:37Z[36m [INFO][SMF][GIN] [0m| 200 |  10.233.102.168 | POST    | /nsmf-pdusession/v1/sm-contexts/urn:uuid:48581a9b-4978-4989-8d4e-2dc67b8d5e61/modify |
Defaulted container "smf" out of: smf, wait-nrf (init)

### AMF LOGS (NGAP)
No resources found in ns-1274485 namespace.

## RAN / UE
UE POD: ueransim-singlepod-7c48f47d7-xwxh9
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0@if127: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 qdisc noqueue state UP group default qlen 1000
    link/ether 52:84:12:b3:a1:ea brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 10.233.75.20/32 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::5084:12ff:feb3:a1ea/64 scope link 
       valid_lft forever preferred_lft forever
3: uesimtun0: <POINTOPOINT,PROMISC,NOTRAILERS,UP,LOWER_UP> mtu 1400 qdisc fq_codel state UNKNOWN group default qlen 500
    link/none 
    inet 10.1.0.1/24 scope global uesimtun0
       valid_lft forever preferred_lft forever
    inet6 fe80::272:9d70:1ba3:9a1e/64 scope link stable-privacy 
       valid_lft forever preferred_lft forever
default via 169.254.1.1 dev eth0 
10.1.0.0/24 dev uesimtun0 proto kernel scope link src 10.1.0.1 
169.254.1.1 dev eth0 scope link 

## TRANSPORT (ONOS / MININET)
nasp-transport       onos-fb87c586c-6rp4l                                              1/1     Running             0                 42h

## N6 (MULTUS)
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0@if125: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 qdisc noqueue state UP group default qlen 1000
    link/ether f6:68:f1:db:77:07 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 10.233.75.25/32 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::f468:f1ff:fedb:7707/64 scope link 
       valid_lft forever preferred_lft forever
3: net1@if126: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 0e:e5:37:21:02:31 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 192.168.100.61/24 brd 192.168.100.255 scope global net1
       valid_lft forever preferred_lft forever
    inet6 fe80::ce5:37ff:fe21:231/64 scope link 
       valid_lft forever preferred_lft forever
4: upfgtp: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
    link/none 
    inet6 fe80::4383:5cbc:ed28:b1a4/64 scope link stable-privacy 
       valid_lft forever preferred_lft forever
default via 169.254.1.1 dev eth0 
10.1.0.0/17 dev upfgtp proto static 
169.254.1.1 dev eth0 scope link 
192.168.100.0/24 dev net1 proto kernel scope link src 192.168.100.61 

## TRI-SLA CONFIG
apiVersion: v1
items:
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "17"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-02-17T00:49:00Z"
    generation: 17
    labels:
      app: kafka
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: kafka
      app.kubernetes.io/part-of: trisla
    name: kafka
    namespace: trisla
    resourceVersion: "886041481"
    uid: c45b19d2-08f8-480e-b103-008c17ab85e5
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: kafka
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-02-17T11:05:09-03:00"
        creationTimestamp: null
        labels:
          app: kafka
          app.kubernetes.io/name: kafka
          app.kubernetes.io/part-of: trisla
      spec:
        containers:
        - env:
          - name: KAFKA_NODE_ID
            value: "1"
          - name: KAFKA_PROCESS_ROLES
            value: broker,controller
          - name: KAFKA_CONTROLLER_QUORUM_VOTERS
            value: 1@localhost:9093
          - name: KAFKA_LISTENERS
            value: PLAINTEXT://:9092,CONTROLLER://:9093
          - name: KAFKA_ADVERTISED_LISTENERS
            value: PLAINTEXT://kafka.trisla.svc.cluster.local:9092
          - name: KAFKA_LISTENER_SECURITY_PROTOCOL_MAP
            value: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
          - name: KAFKA_CONTROLLER_LISTENER_NAMES
            value: CONTROLLER
          - name: KAFKA_LOG_DIRS
            value: /tmp/kraft-combined-logs
          image: ghcr.io/abelisboa/trisla-kafka@sha256:8291bed273105a3fc88df5f89096abf6a654dc92b0937245dcef85011f3fc5e6
          imagePullPolicy: IfNotPresent
          name: kafka
          ports:
          - containerPort: 9092
            name: kafka
            protocol: TCP
          resources:
            limits:
              cpu: "1"
              memory: 1Gi
            requests:
              cpu: 200m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-02-25T23:30:39Z"
      lastUpdateTime: "2026-03-02T23:00:58Z"
      message: ReplicaSet "kafka-6bd4bcdc7b" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-11T02:42:03Z"
      lastUpdateTime: "2026-04-11T02:42:03Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 17
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "11"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"trisla-analytics-adapter","namespace":"trisla"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"trisla-analytics-adapter"}},"template":{"metadata":{"labels":{"app":"trisla-analytics-adapter"}},"spec":{"containers":[{"args":["pip install --no-cache-dir fastapi==0.111.0 uvicorn[standard]==0.30.0 prometheus_client==0.20.0 requests==2.32.3\ncd /app \u0026\u0026 uvicorn main:app --host 0.0.0.0 --port 8080\n"],"command":["/bin/sh","-c"],"env":[{"name":"PROMETHEUS_URL","value":"http://monitoring-kube-prometheus-prometheus.monitoring:9090"},{"name":"CORE5G_NAMESPACE","value":"ns-1274485"},{"name":"RAN_NAMESPACE","value":"ns-1274485"},{"name":"RAN_POD","value":"rantester-0"},{"name":"PYTHONUNBUFFERED","value":"1"}],"image":"python:3.11-slim","name":"adapter","ports":[{"containerPort":8080,"name":"http"}],"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"volumeMounts":[{"mountPath":"/app","name":"code"}]}],"volumes":[{"configMap":{"name":"trisla-analytics-adapter-code"},"name":"code"}]}}}}
    creationTimestamp: "2026-01-30T18:30:03Z"
    generation: 11
    name: trisla-analytics-adapter
    namespace: trisla
    resourceVersion: "886041504"
    uid: 59054670-3b71-402b-ba98-123c407dba70
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-analytics-adapter
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-03-08T20:48:20-03:00"
        creationTimestamp: null
        labels:
          app: trisla-analytics-adapter
      spec:
        containers:
        - args:
          - |
            pip install --no-cache-dir fastapi==0.111.0 uvicorn[standard]==0.30.0 prometheus_client==0.20.0 requests==2.32.3
            cd /app && uvicorn main:app --host 0.0.0.0 --port 8080
          command:
          - /bin/sh
          - -c
          env:
          - name: PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090
          - name: CORE5G_NAMESPACE
            value: ns-1274485
          - name: RAN_NAMESPACE
            value: ns-1274485
          - name: RAN_POD
            value: rantester-0
          - name: PYTHONUNBUFFERED
            value: "1"
          - name: TRISLA_PROM_ENABLED
            value: "true"
          - name: PROM_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090
          - name: PROM_HOST
            value: prometheus-kube-prometheus-prometheus.monitoring.svc
          - name: PROM_PORT
            value: "9090"
          image: python:3.11-slim
          imagePullPolicy: IfNotPresent
          name: adapter
          ports:
          - containerPort: 8080
            name: http
            protocol: TCP
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 128Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          volumeMounts:
          - mountPath: /app
            name: code
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
        volumes:
        - configMap:
            defaultMode: 420
            name: trisla-analytics-adapter-code
          name: code
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-01-30T18:30:03Z"
      lastUpdateTime: "2026-03-08T23:48:22Z"
      message: ReplicaSet "trisla-analytics-adapter-86594d5b8f" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-11T02:42:03Z"
      lastUpdateTime: "2026-04-11T02:42:03Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 11
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "39"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-02-14T21:18:35Z"
    generation: 43
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-bc-nssmf
    namespace: trisla
    resourceVersion: "886497725"
    uid: ab2b178c-fe45-4c01-99c4-7979365bf5ce
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-bc-nssmf
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-02-17T19:52:51-03:00"
        creationTimestamp: null
        labels:
          app: trisla-bc-nssmf
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: BC_ENABLED
            value: "true"
          - name: BC_RPC_URL
            value: http://trisla-besu.trisla.svc.cluster.local:8545
          - name: TRISLA_RPC_URL
            value: http://trisla-besu.trisla.svc.cluster.local:8545
          - name: BESU_RPC_URL
            value: http://trisla-besu.trisla.svc.cluster.local:8545
          - name: TRISLA_CHAIN_ID
            value: "1337"
          - name: BC_PRIVATE_KEY_PATH
            value: /secrets/bc/privateKey
          - name: BC_PRIVATE_KEY
            valueFrom:
              secretKeyRef:
                key: privateKey
                name: bc-nssmf-wallet
          - name: CONTRACT_ADDRESS_PATH
            value: /app/src/contracts/contract_address.json
          - name: BC_TX_RECEIPT_TIMEOUT
            value: "120"
          image: ghcr.io/abelisboa/trisla-bc-nssmf@sha256:b0db5eef2128baddee2c1c3ea72fb5fec421afb1d87407e5f4a6aadd75f9f95a
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 30
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          name: bc-nssmf
          ports:
          - containerPort: 8083
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /health/ready
              port: http
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 1
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          volumeMounts:
          - mountPath: /secrets/bc
            name: bc-wallet
            readOnly: true
          - mountPath: /app/src/contracts
            name: bc-contract
            readOnly: true
        dnsPolicy: ClusterFirst
        nodeSelector:
          kubernetes.io/hostname: node2
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
        volumes:
        - name: bc-wallet
          secret:
            defaultMode: 420
            secretName: bc-nssmf-wallet
        - configMap:
            defaultMode: 420
            name: trisla-bc-contract-address
          name: bc-contract
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-09T18:20:29Z"
      lastUpdateTime: "2026-04-06T01:47:14Z"
      message: ReplicaSet "trisla-bc-nssmf-599b574f74" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:03:35Z"
      lastUpdateTime: "2026-04-12T21:03:35Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 43
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "16"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-01-31T19:45:37Z"
    generation: 36
    labels:
      app: besu
      app.kubernetes.io/component: besu
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      component: blockchain
      helm.sh/chart: trisla-3.10.0
    name: trisla-besu
    namespace: trisla
    resourceVersion: "886497693"
    uid: c9a9bbc6-b0f7-4a00-a685-d77be89ac32e
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: besu
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
        component: blockchain
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        creationTimestamp: null
        labels:
          app: besu
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
          component: blockchain
      spec:
        containers:
        - args:
          - --genesis-file=/data/genesis.json
          - --data-path=/opt/besu/data
          - --rpc-http-enabled=true
          - --rpc-http-host=0.0.0.0
          - --rpc-http-port=8545
          - --rpc-http-api=ETH,NET,WEB3,ADMIN,MINER
          - --host-allowlist=*
          - --rpc-http-cors-origins=*
          - --min-gas-price=0
          command:
          - /opt/besu/bin/besu
          env:
          - name: BESU_DATA_PATH
            value: /opt/besu/data
          image: ghcr.io/abelisboa/trisla-besu@sha256:ab84d26d678417b615c0833b4a34e9fe2778cec392a7e23596fa1607cf362efc
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 6
            initialDelaySeconds: 30
            periodSeconds: 20
            successThreshold: 1
            tcpSocket:
              port: 8545
            timeoutSeconds: 5
          name: besu
          ports:
          - containerPort: 8545
            name: rpc-http
            protocol: TCP
          - containerPort: 8546
            name: rpc-ws
            protocol: TCP
          - containerPort: 30303
            name: p2p
            protocol: TCP
          readinessProbe:
            failureThreshold: 6
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            tcpSocket:
              port: 8545
            timeoutSeconds: 3
          resources:
            limits:
              cpu: "4"
              memory: 8Gi
            requests:
              cpu: "1"
              memory: 2Gi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          volumeMounts:
          - mountPath: /opt/besu/data
            name: besu-data
          - mountPath: /data
            name: genesis
            readOnly: true
        dnsPolicy: ClusterFirst
        initContainers:
        - command:
          - sh
          - -c
          - cp /secrets/key /opt/besu/data/key && chmod 600 /opt/besu/data/key
          image: ghcr.io/abelisboa/trisla-besu@sha256:ab84d26d678417b615c0833b4a34e9fe2778cec392a7e23596fa1607cf362efc
          imagePullPolicy: IfNotPresent
          name: copy-validator-key
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          volumeMounts:
          - mountPath: /opt/besu/data
            name: besu-data
          - mountPath: /secrets
            name: validator-key
            readOnly: true
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
        volumes:
        - name: besu-data
          persistentVolumeClaim:
            claimName: trisla-besu-data
        - configMap:
            defaultMode: 420
            name: trisla-besu-genesis
          name: genesis
        - name: validator-key
          secret:
            defaultMode: 420
            secretName: trisla-besu-validator-key
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-03T02:49:07Z"
      lastUpdateTime: "2026-03-03T02:49:07Z"
      message: ReplicaSet "trisla-besu-756cf5ff69" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:03:32Z"
      lastUpdateTime: "2026-04-12T21:03:32Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 36
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "2"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"trisla-blockchain-exporter"},"name":"trisla-blockchain-exporter","namespace":"trisla"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"trisla-blockchain-exporter"}},"template":{"metadata":{"labels":{"app":"trisla-blockchain-exporter"}},"spec":{"containers":[{"env":[{"name":"BESU_RPC_URL","value":"http://besu:8545"}],"image":"ghcr.io/abelisboa/trisla-blockchain-exporter@sha256:cae3600a15294a41295928d2ec1814561d66ded42d0945d8da10870a5c0e4a3d","imagePullPolicy":"IfNotPresent","name":"exporter","ports":[{"containerPort":8000}]}]}}}}
    creationTimestamp: "2026-03-04T14:24:12Z"
    generation: 2
    labels:
      app: trisla-blockchain-exporter
    name: trisla-blockchain-exporter
    namespace: trisla
    resourceVersion: "886041493"
    uid: ea7ae36b-2cca-4f91-b713-62552f035a0c
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-blockchain-exporter
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        creationTimestamp: null
        labels:
          app: trisla-blockchain-exporter
      spec:
        containers:
        - env:
          - name: BESU_RPC_URL
            value: http://besu:8545
          image: ghcr.io/abelisboa/trisla-blockchain-exporter@sha256:cae3600a15294a41295928d2ec1814561d66ded42d0945d8da10870a5c0e4a3d
          imagePullPolicy: IfNotPresent
          name: exporter
          ports:
          - containerPort: 8000
            protocol: TCP
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-04T14:24:12Z"
      lastUpdateTime: "2026-03-04T18:37:36Z"
      message: ReplicaSet "trisla-blockchain-exporter-75776c777f" has successfully
        progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-11T02:42:03Z"
      lastUpdateTime: "2026-04-11T02:42:03Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 2
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "102"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-02-14T21:18:35Z"
    generation: 110
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-decision-engine
    namespace: trisla
    resourceVersion: "886436927"
    uid: 9c729c31-641e-4d04-8e96-d27219ac1724
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-decision-engine
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          force-redeploy: "1772072617"
          kubectl.kubernetes.io/restartedAt: "2026-02-24T23:05:42-03:00"
        creationTimestamp: null
        labels:
          app: trisla-decision-engine
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: GATE_3GPP_ENABLED
            value: "false"
          - name: LOG_LEVEL
            value: DEBUG
          - name: ML_NSMF_HTTP_URL
            value: http://trisla-ml-nsmf:8081
          - name: SLA_AGENT_URL
            value: http://trisla-sla-agent-layer:8084
          - name: OTLP_ENABLED
            value: "true"
          - name: PRB_RISK_ALPHA
            value: "0.15"
          - name: POLICY_GOVERNED_MODE
            value: "true"
          - name: ML_CAN_OVERRIDE_REJECT
            value: "false"
          - name: ML_REFINEMENT_CONFIDENCE
            value: "0.20"
          - name: HARD_PRB_REJECT_THRESHOLD
            value: "25"
          - name: HARD_PRB_RENEGOTIATE_THRESHOLD
            value: "15"
          - name: DECISION_SCORE_MODE
            value: "true"
          image: ghcr.io/abelisboa/trisla-decision-engine@sha256:ae2919354aff9d2a1c95a1a7096f1f3d96403b03bbb3603bab29fae2a643d39c
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 6
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 30
            periodSeconds: 15
            successThreshold: 1
            timeoutSeconds: 5
          name: decision-engine
          ports:
          - containerPort: 8082
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 6
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 15
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        serviceAccount: default
        serviceAccountName: default
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-06T01:25:05Z"
      lastUpdateTime: "2026-04-06T01:25:05Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-03-30T04:13:55Z"
      lastUpdateTime: "2026-04-12T15:23:31Z"
      message: ReplicaSet "trisla-decision-engine-78b689465d" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 110
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "2"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"trisla","app.kubernetes.io/managed-by":"Helm","app.kubernetes.io/name":"trisla","helm.sh/chart":"trisla-3.10.0"},"name":"trisla-decision-engine-trisla","namespace":"trisla"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":10,"selector":{"matchLabels":{"app":"trisla-decision-engine-trisla","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"force-redeploy":"1772072617","kubectl.kubernetes.io/restartedAt":"2026-02-24T23:05:42-03:00"},"creationTimestamp":null,"labels":{"app":"trisla-decision-engine-trisla","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"spec":{"containers":[{"env":[{"name":"TRISLA_NODE_INTERFACE","value":"my5g"},{"name":"TRISLA_NODE_IP","value":"192.168.10.16"},{"name":"OTLP_ENDPOINT","value":"http://trisla-otel-collector:4317"},{"name":"GATE_3GPP_ENABLED","value":"false"},{"name":"LOG_LEVEL","value":"DEBUG"},{"name":"ML_NSMF_HTTP_URL","value":"http://trisla-ml-nsmf:8081"},{"name":"SLA_AGENT_URL","value":"http://trisla-sla-agent-layer:8084"},{"name":"OTLP_ENABLED","value":"true"},{"name":"PRB_RISK_ALPHA","value":"0.92"},{"name":"POLICY_GOVERNED_MODE","value":"true"},{"name":"ML_CAN_OVERRIDE_REJECT","value":"false"},{"name":"ML_REFINEMENT_CONFIDENCE","value":"0.6"},{"name":"HARD_PRB_REJECT_THRESHOLD","value":"22"},{"name":"HARD_PRB_RENEGOTIATE_THRESHOLD","value":"16"}],"image":"ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f","imagePullPolicy":"IfNotPresent","livenessProbe":{"failureThreshold":6,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":30,"periodSeconds":15,"successThreshold":1,"timeoutSeconds":5},"name":"decision-engine","ports":[{"containerPort":8082,"name":"http","protocol":"TCP"}],"readinessProbe":{"failureThreshold":6,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":15,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"resources":{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"500m","memory":"512Mi"}},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"serviceAccount":"default","serviceAccountName":"default","terminationGracePeriodSeconds":30}}}}
    creationTimestamp: "2026-04-09T17:30:28Z"
    generation: 2
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-decision-engine-trisla
    namespace: trisla
    resourceVersion: "886437045"
    uid: 0632b69d-d21d-4914-a627-fc232c5137f6
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-decision-engine-trisla
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          force-redeploy: "1772072617"
          kubectl.kubernetes.io/restartedAt: "2026-02-24T23:05:42-03:00"
        creationTimestamp: null
        labels:
          app: trisla-decision-engine-trisla
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: GATE_3GPP_ENABLED
            value: "false"
          - name: LOG_LEVEL
            value: DEBUG
          - name: ML_NSMF_HTTP_URL
            value: http://trisla-ml-nsmf:8081
          - name: SLA_AGENT_URL
            value: http://trisla-sla-agent-layer:8084
          - name: OTLP_ENABLED
            value: "true"
          - name: PRB_RISK_ALPHA
            value: "0.92"
          - name: POLICY_GOVERNED_MODE
            value: "true"
          - name: ML_CAN_OVERRIDE_REJECT
            value: "false"
          - name: ML_REFINEMENT_CONFIDENCE
            value: "0.6"
          - name: HARD_PRB_REJECT_THRESHOLD
            value: "25"
          - name: HARD_PRB_RENEGOTIATE_THRESHOLD
            value: "15"
          image: ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 6
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 30
            periodSeconds: 15
            successThreshold: 1
            timeoutSeconds: 5
          name: decision-engine
          ports:
          - containerPort: 8082
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 6
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 15
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        serviceAccount: default
        serviceAccountName: default
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-09T17:30:49Z"
      lastUpdateTime: "2026-04-09T17:30:49Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-04-09T17:30:28Z"
      lastUpdateTime: "2026-04-12T15:23:57Z"
      message: ReplicaSet "trisla-decision-engine-trisla-6649f6cc78" has successfully
        progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 2
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "1"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"trisla","app.kubernetes.io/managed-by":"Helm","app.kubernetes.io/name":"trisla","helm.sh/chart":"trisla-3.10.0"},"name":"trisla-decision-engine-v1","namespace":"trisla"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":10,"selector":{"matchLabels":{"app":"trisla-decision-engine-v1","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"force-redeploy":"1772072617","kubectl.kubernetes.io/restartedAt":"2026-02-24T23:05:42-03:00"},"creationTimestamp":null,"labels":{"app":"trisla-decision-engine-v1","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"spec":{"containers":[{"env":[{"name":"TRISLA_NODE_INTERFACE","value":"my5g"},{"name":"TRISLA_NODE_IP","value":"192.168.10.16"},{"name":"OTLP_ENDPOINT","value":"http://trisla-otel-collector:4317"},{"name":"GATE_3GPP_ENABLED","value":"false"},{"name":"LOG_LEVEL","value":"DEBUG"},{"name":"ML_NSMF_HTTP_URL","value":"http://trisla-ml-nsmf:8081"},{"name":"SLA_AGENT_URL","value":"http://trisla-sla-agent-layer:8084"},{"name":"OTLP_ENABLED","value":"true"},{"name":"PRB_RISK_ALPHA","value":"0.92"},{"name":"POLICY_GOVERNED_MODE","value":"false"},{"name":"ML_CAN_OVERRIDE_REJECT","value":"false"},{"name":"ML_REFINEMENT_CONFIDENCE","value":"99"},{"name":"HARD_PRB_REJECT_THRESHOLD","value":"22"},{"name":"HARD_PRB_RENEGOTIATE_THRESHOLD","value":"16"}],"image":"ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f","imagePullPolicy":"IfNotPresent","livenessProbe":{"failureThreshold":6,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":30,"periodSeconds":15,"successThreshold":1,"timeoutSeconds":5},"name":"decision-engine","ports":[{"containerPort":8082,"name":"http","protocol":"TCP"}],"readinessProbe":{"failureThreshold":6,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":15,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"resources":{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"500m","memory":"512Mi"}},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"serviceAccount":"default","serviceAccountName":"default","terminationGracePeriodSeconds":30}}}}
    creationTimestamp: "2026-04-09T17:30:28Z"
    generation: 1
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-decision-engine-v1
    namespace: trisla
    resourceVersion: "885696842"
    uid: 2022b17a-7bec-4796-b5a5-0b169b2409af
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-decision-engine-v1
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          force-redeploy: "1772072617"
          kubectl.kubernetes.io/restartedAt: "2026-02-24T23:05:42-03:00"
        creationTimestamp: null
        labels:
          app: trisla-decision-engine-v1
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: GATE_3GPP_ENABLED
            value: "false"
          - name: LOG_LEVEL
            value: DEBUG
          - name: ML_NSMF_HTTP_URL
            value: http://trisla-ml-nsmf:8081
          - name: SLA_AGENT_URL
            value: http://trisla-sla-agent-layer:8084
          - name: OTLP_ENABLED
            value: "true"
          - name: PRB_RISK_ALPHA
            value: "0.92"
          - name: POLICY_GOVERNED_MODE
            value: "false"
          - name: ML_CAN_OVERRIDE_REJECT
            value: "false"
          - name: ML_REFINEMENT_CONFIDENCE
            value: "99"
          - name: HARD_PRB_REJECT_THRESHOLD
            value: "22"
          - name: HARD_PRB_RENEGOTIATE_THRESHOLD
            value: "16"
          image: ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 6
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 30
            periodSeconds: 15
            successThreshold: 1
            timeoutSeconds: 5
          name: decision-engine
          ports:
          - containerPort: 8082
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 6
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 15
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        serviceAccount: default
        serviceAccountName: default
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-09T17:30:48Z"
      lastUpdateTime: "2026-04-09T17:30:48Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-04-09T17:30:28Z"
      lastUpdateTime: "2026-04-09T17:30:48Z"
      message: ReplicaSet "trisla-decision-engine-v1-7d69f8bbf5" has successfully
        progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 1
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "1"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"trisla","app.kubernetes.io/managed-by":"Helm","app.kubernetes.io/name":"trisla","helm.sh/chart":"trisla-3.10.0"},"name":"trisla-decision-engine-v2","namespace":"trisla"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":10,"selector":{"matchLabels":{"app":"trisla-decision-engine-v2","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"force-redeploy":"1772072617","kubectl.kubernetes.io/restartedAt":"2026-02-24T23:05:42-03:00"},"creationTimestamp":null,"labels":{"app":"trisla-decision-engine-v2","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"spec":{"containers":[{"env":[{"name":"TRISLA_NODE_INTERFACE","value":"my5g"},{"name":"TRISLA_NODE_IP","value":"192.168.10.16"},{"name":"OTLP_ENDPOINT","value":"http://trisla-otel-collector:4317"},{"name":"GATE_3GPP_ENABLED","value":"false"},{"name":"LOG_LEVEL","value":"DEBUG"},{"name":"ML_NSMF_HTTP_URL","value":"http://trisla-ml-nsmf:8081"},{"name":"SLA_AGENT_URL","value":"http://trisla-sla-agent-layer:8084"},{"name":"OTLP_ENABLED","value":"true"},{"name":"PRB_RISK_ALPHA","value":"0.92"},{"name":"POLICY_GOVERNED_MODE","value":"false"},{"name":"ML_CAN_OVERRIDE_REJECT","value":"false"},{"name":"ML_REFINEMENT_CONFIDENCE","value":"0.2"},{"name":"HARD_PRB_REJECT_THRESHOLD","value":"22"},{"name":"HARD_PRB_RENEGOTIATE_THRESHOLD","value":"16"}],"image":"ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f","imagePullPolicy":"IfNotPresent","livenessProbe":{"failureThreshold":6,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":30,"periodSeconds":15,"successThreshold":1,"timeoutSeconds":5},"name":"decision-engine","ports":[{"containerPort":8082,"name":"http","protocol":"TCP"}],"readinessProbe":{"failureThreshold":6,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":15,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"resources":{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"500m","memory":"512Mi"}},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"serviceAccount":"default","serviceAccountName":"default","terminationGracePeriodSeconds":30}}}}
    creationTimestamp: "2026-04-09T17:30:28Z"
    generation: 1
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-decision-engine-v2
    namespace: trisla
    resourceVersion: "885696848"
    uid: f9586ea8-a78f-4e10-bfd8-df98d7af9831
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-decision-engine-v2
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          force-redeploy: "1772072617"
          kubectl.kubernetes.io/restartedAt: "2026-02-24T23:05:42-03:00"
        creationTimestamp: null
        labels:
          app: trisla-decision-engine-v2
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: GATE_3GPP_ENABLED
            value: "false"
          - name: LOG_LEVEL
            value: DEBUG
          - name: ML_NSMF_HTTP_URL
            value: http://trisla-ml-nsmf:8081
          - name: SLA_AGENT_URL
            value: http://trisla-sla-agent-layer:8084
          - name: OTLP_ENABLED
            value: "true"
          - name: PRB_RISK_ALPHA
            value: "0.92"
          - name: POLICY_GOVERNED_MODE
            value: "false"
          - name: ML_CAN_OVERRIDE_REJECT
            value: "false"
          - name: ML_REFINEMENT_CONFIDENCE
            value: "0.2"
          - name: HARD_PRB_REJECT_THRESHOLD
            value: "22"
          - name: HARD_PRB_RENEGOTIATE_THRESHOLD
            value: "16"
          image: ghcr.io/abelisboa/trisla-decision-engine@sha256:2ba19ee1197f29a51b3886ee6d0841327a817bc611315219ef40459006d8c31f
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 6
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 30
            periodSeconds: 15
            successThreshold: 1
            timeoutSeconds: 5
          name: decision-engine
          ports:
          - containerPort: 8082
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 6
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 15
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        serviceAccount: default
        serviceAccountName: default
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-09T17:30:48Z"
      lastUpdateTime: "2026-04-09T17:30:48Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-04-09T17:30:28Z"
      lastUpdateTime: "2026-04-09T17:30:48Z"
      message: ReplicaSet "trisla-decision-engine-v2-7657ff4c68" has successfully
        progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 1
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "2"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"trisla-iperf3-server","namespace":"trisla"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"trisla-iperf3-server"}},"template":{"metadata":{"labels":{"app":"trisla-iperf3-server"}},"spec":{"containers":[{"args":["-s"],"image":"networkstatic/iperf3","name":"iperf3","ports":[{"containerPort":5201}]}]}}}}
    creationTimestamp: "2026-01-21T22:34:15Z"
    generation: 2
    name: trisla-iperf3-server
    namespace: trisla
    resourceVersion: "886496924"
    uid: 33545bb6-22c2-40ec-98d9-0cba4ab09d6e
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-iperf3-server
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-01-22T11:56:51-03:00"
        creationTimestamp: null
        labels:
          app: trisla-iperf3-server
      spec:
        containers:
        - args:
          - -s
          image: networkstatic/iperf3
          imagePullPolicy: Always
          name: iperf3
          ports:
          - containerPort: 5201
            protocol: TCP
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-01-21T22:34:15Z"
      lastUpdateTime: "2026-01-22T14:57:28Z"
      message: ReplicaSet "trisla-iperf3-server-76f599c648" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:02:16Z"
      lastUpdateTime: "2026-04-12T21:02:16Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 2
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "49"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-02-14T21:18:35Z"
    generation: 51
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-ml-nsmf
    namespace: trisla
    resourceVersion: "886497716"
    uid: 65cfc3b0-e117-4e6d-bcde-8a1a1d14d5e4
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-ml-nsmf
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-05T22:48:50-03:00"
        creationTimestamp: null
        labels:
          app: trisla-ml-nsmf
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: KAFKA_ENABLED
            value: "true"
          - name: KAFKA_BROKERS
            value: kafka:9092
          - name: OTLP_ENABLED
            value: "true"
          - name: ML_DECISION_CLASSIFIER_PATH
            value: /app/models/decision_classifier.pkl
          image: ghcr.io/abelisboa/trisla-ml-nsmf@sha256:0e6f14940b753626cf5c2057bf6a6a2633c8b0ddc7cc913abaf6253aa40ace3e
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 30
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          name: ml-nsmf
          ports:
          - containerPort: 8081
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 1
          resources:
            limits:
              cpu: "4"
              memory: 4Gi
            requests:
              cpu: "1"
              memory: 1Gi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        nodeSelector:
          kubernetes.io/hostname: node2
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-24T22:55:06Z"
      lastUpdateTime: "2026-04-06T01:47:15Z"
      message: ReplicaSet "trisla-ml-nsmf-64c6c7f96" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:03:34Z"
      lastUpdateTime: "2026-04-12T21:03:34Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 51
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "146"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2025-12-19T17:28:59Z"
    generation: 153
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-nasp-adapter
    namespace: trisla
    resourceVersion: "886497755"
    uid: 931b57f5-801f-4a1a-94cd-a01213b7ff78
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-nasp-adapter
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-05T22:48:50-03:00"
        creationTimestamp: null
        labels:
          app: trisla-nasp-adapter
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        automountServiceAccountToken: true
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: SEM_CSMF_URL
            value: http://trisla-sem-csmf.trisla.svc.cluster.local:8080
          - name: WORKLOAD_PROVISIONING_ENABLED
            value: "true"
          - name: WORKLOAD_TIMEOUT_SECONDS
            value: "90"
          - name: EMBB_CPU
            value: "64"
          - name: EMBB_MEM
            value: 128Gi
          - name: WORKLOAD_IMAGE
            value: polinux/stress:latest
          - name: OTEL_EXPORTER_OTLP_INSECURE
            value: "true"
          - name: OTEL_EXPORTER_OTLP_PROTOCOL
            value: grpc
          - name: OTEL_EXPORTER_OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: OTEL_TRACES_SAMPLER
            value: always_on
          - name: OTEL_TRACES_EXPORTER
            value: otlp
          - name: OTLP_ENABLED
            value: "true"
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: GATE_3GPP_ENABLED
            value: "true"
          - name: GATE_3GPP_CORE_NAMESPACE
            value: ns-1274485
          - name: GATE_3GPP_UERANSIM_NAMESPACE
            value: ueransim
          - name: UPF_MAX_SESSIONS
            value: "1000000"
          - name: CAPACITY_ACCOUNTING_ENABLED
            value: "true"
          - name: RESERVATION_TTL_SECONDS
            value: "300"
          - name: RECONCILE_INTERVAL_SECONDS
            value: "60"
          - name: CAPACITY_SAFETY_FACTOR
            value: "0.1"
          - name: COST_EMBB_CORE
            value: "1"
          - name: COST_EMBB_RAN
            value: "1"
          - name: COST_EMBB_TRANSPORT
            value: "1"
          - name: COST_URLLC_CORE
            value: "1"
          - name: COST_URLLC_RAN
            value: "1"
          - name: COST_URLLC_TRANSPORT
            value: "1"
          - name: COST_MMTC_CORE
            value: "1"
          - name: COST_MMTC_RAN
            value: "1"
          - name: COST_MMTC_TRANSPORT
            value: "1"
          - name: PROMETHEUS_URL
            value: http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: TRISLA_TRANSPORT_SDN_ENABLED
            value: "true"
          - name: ONOS_REST_URL
            value: http://onos.nasp-transport.svc.cluster.local:8181
          - name: TRISLA_TRANSPORT_ONOS_PRUNE_CLI_INTENTS
            value: "true"
          image: ghcr.io/abelisboa/trisla-nasp-adapter@sha256:063bddea5a6fcb38d8de504f91cc63b9ab13d5369dff43b6742cc5ae3ab02d79
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 30
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          name: nasp-adapter
          ports:
          - containerPort: 8085
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 1
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        nodeSelector:
          kubernetes.io/hostname: node2
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        serviceAccount: trisla-nasp-adapter
        serviceAccountName: trisla-nasp-adapter
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-03T02:49:07Z"
      lastUpdateTime: "2026-04-11T18:43:28Z"
      message: ReplicaSet "trisla-nasp-adapter-6f79f5446b" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:03:39Z"
      lastUpdateTime: "2026-04-12T21:03:39Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 153
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "2"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"trisla-network-exporter"},"name":"trisla-network-exporter","namespace":"trisla"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"trisla-network-exporter"}},"template":{"metadata":{"labels":{"app":"trisla-network-exporter"}},"spec":{"containers":[{"env":[{"name":"IPERF_SERVER","value":"localhost"},{"name":"IPERF_PORT","value":"5201"}],"image":"ghcr.io/abelisboa/trisla-network-exporter@sha256:c17d33431ea923120899ff1d9f5b6561183dd07cc392e5ccf0340b2898a5ba95","imagePullPolicy":"IfNotPresent","name":"exporter","ports":[{"containerPort":8000}]}]}}}}
    creationTimestamp: "2026-03-04T14:24:12Z"
    generation: 2
    labels:
      app: trisla-network-exporter
    name: trisla-network-exporter
    namespace: trisla
    resourceVersion: "886041466"
    uid: 1cd9ab5d-a595-4492-bff6-1aa0b468c131
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-network-exporter
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        creationTimestamp: null
        labels:
          app: trisla-network-exporter
      spec:
        containers:
        - env:
          - name: IPERF_SERVER
            value: localhost
          - name: IPERF_PORT
            value: "5201"
          image: ghcr.io/abelisboa/trisla-network-exporter@sha256:c17d33431ea923120899ff1d9f5b6561183dd07cc392e5ccf0340b2898a5ba95
          imagePullPolicy: IfNotPresent
          name: exporter
          ports:
          - containerPort: 8000
            protocol: TCP
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-04T14:24:12Z"
      lastUpdateTime: "2026-03-04T18:37:33Z"
      message: ReplicaSet "trisla-network-exporter-6d8b4d4495" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-11T02:42:03Z"
      lastUpdateTime: "2026-04-11T02:42:03Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 2
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "2"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"trisla-otel-collector","namespace":"trisla"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"trisla-otel-collector"}},"template":{"metadata":{"labels":{"app":"trisla-otel-collector"}},"spec":{"containers":[{"args":["--config=/etc/otel/otel-collector-config.yaml"],"image":"otel/opentelemetry-collector:0.92.0","livenessProbe":{"initialDelaySeconds":10,"periodSeconds":10,"tcpSocket":{"port":4317}},"name":"otel-collector","ports":[{"containerPort":4317},{"containerPort":4318}],"readinessProbe":{"initialDelaySeconds":5,"periodSeconds":5,"tcpSocket":{"port":4317}},"resources":{"limits":{"cpu":"1000m","memory":"1Gi"},"requests":{"cpu":"200m","memory":"256Mi"}},"volumeMounts":[{"mountPath":"/etc/otel","name":"config"}]}],"volumes":[{"configMap":{"name":"trisla-otel-config"},"name":"config"}]}}}}
    creationTimestamp: "2026-02-25T00:55:08Z"
    generation: 2
    name: trisla-otel-collector
    namespace: trisla
    resourceVersion: "886497081"
    uid: 84824c66-5641-4946-b6e8-b7d2329a84d2
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-otel-collector
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-02-24T22:18:09-03:00"
        creationTimestamp: null
        labels:
          app: trisla-otel-collector
      spec:
        containers:
        - args:
          - --config=/etc/otel/otel-collector-config.yaml
          image: otel/opentelemetry-collector:0.92.0
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 3
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            tcpSocket:
              port: 4317
            timeoutSeconds: 1
          name: otel-collector
          ports:
          - containerPort: 4317
            protocol: TCP
          - containerPort: 4318
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            initialDelaySeconds: 5
            periodSeconds: 5
            successThreshold: 1
            tcpSocket:
              port: 4317
            timeoutSeconds: 1
          resources:
            limits:
              cpu: "1"
              memory: 1Gi
            requests:
              cpu: 200m
              memory: 256Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          volumeMounts:
          - mountPath: /etc/otel
            name: config
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
        volumes:
        - configMap:
            defaultMode: 420
            name: trisla-otel-config
          name: config
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-02-25T00:55:08Z"
      lastUpdateTime: "2026-02-25T01:18:19Z"
      message: ReplicaSet "trisla-otel-collector-859cc8466f" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:02:29Z"
      lastUpdateTime: "2026-04-12T21:02:29Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 2
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "213"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{"deployment.kubernetes.io/revision":"110","meta.helm.sh/release-name":"trisla-portal","meta.helm.sh/release-namespace":"trisla"},"creationTimestamp":"2026-03-06T13:07:39Z","generation":138,"labels":{"app":"trisla-portal-backend","app.kubernetes.io/managed-by":"Helm","component":"backend"},"name":"trisla-portal-backend","namespace":"trisla","resourceVersion":"882421565","uid":"0fd09586-cc4e-4938-8180-e8cbb3564a0f"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":2,"selector":{"matchLabels":{"app":"trisla-portal-backend"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt":"2026-03-27T23:45:00Z"},"creationTimestamp":null,"labels":{"app":"trisla-portal-backend","component":"backend"}},"spec":{"containers":[{"env":[{"name":"TRISLA_OBS_POLICY_DATASOURCE_SSOT_CM","value":"portal-datasources"},{"name":"TRISLA_OBS_POLICY_NO_REINSTRUMENTATION","value":"true"},{"name":"OBS_OTEL_COLLECTOR_HTTP","value":"http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318"},{"name":"OBS_OTEL_COLLECTOR_GRPC","value":"http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317"},{"name":"OBS_TEMPO_URL","value":"http://trisla-tempo.monitoring.svc.cluster.local:3200"},{"name":"OBS_JAEGER_URL","value":"http://trisla-jaeger.monitoring.svc.cluster.local:16686"},{"name":"OBS_GRAFANA_URL","value":"http://prometheus-grafana.monitoring.svc.cluster.local:80"},{"name":"OBS_PROMETHEUS_URL","value":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"},{"name":"SEM_CSMF_URL","value":"http://trisla-sem-csmf:8080"},{"name":"ML_NSMF_URL","value":"http://trisla-ml-nsmf:8081"},{"name":"DECISION_ENGINE_URL","value":"http://trisla-decision-engine:8082"},{"name":"BC_NSSMF_URL","value":"http://trisla-bc-nssmf:8083"},{"name":"SLA_AGENT_URL","value":"http://trisla-sla-agent-layer:8084"},{"name":"OTEL_SDK_DISABLED"},{"name":"HTTP_TIMEOUT","value":"30"},{"name":"BC_TIMEOUT","value":"60"},{"name":"PROMETHEUS_URL","value":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"},{"name":"TELEMETRY_PROMQL_RAN_LATENCY","value":"avg(trisla_kpi_ran_health)"},{"name":"TELEMETRY_PROMQL_TRANSPORT_RTT","value":"max(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"})*1000"},{"name":"TELEMETRY_PROMQL_CORE_CPU","value":"sum(rate(process_cpu_seconds_total[1m]))"},{"name":"TELEMETRY_PROMQL_CORE_MEMORY","value":"sum(process_resident_memory_bytes)"},{"name":"TELEMETRY_PROMQL_RAN_PRB","value":"avg(trisla_ran_prb_utilization{job=\"trisla-prb-simulator\"})"},{"name":"TELEMETRY_PROMQL_TRANSPORT_JITTER","value":"avg(trisla_transport_jitter_ms{job=\"trisla-prb-simulator\"})"}],"image":"ghcr.io/abelisboa/trisla-portal-backend@sha256:dc112c307ecd7ea448cbea4fc25c8de38877be9b17eff0094bb91fc5305c8d93","imagePullPolicy":"Always","livenessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":8001,"scheme":"HTTP"},"initialDelaySeconds":30,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"name":"backend","ports":[{"containerPort":8001,"name":"http","protocol":"TCP"}],"readinessProbe":{"failureThreshold":3,"httpGet":{"path":"/nasp/diagnostics","port":8001,"scheme":"HTTP"},"initialDelaySeconds":10,"periodSeconds":5,"successThreshold":1,"timeoutSeconds":3},"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"256Mi"}},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","imagePullSecrets":[{"name":"ghcr-secret"}],"restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"terminationGracePeriodSeconds":30}}},"status":{"conditions":[{"lastTransitionTime":"2026-03-27T23:29:33Z","lastUpdateTime":"2026-03-27T23:29:33Z","message":"Deployment does not have minimum availability.","reason":"MinimumReplicasUnavailable","status":"False","type":"Available"},{"lastTransitionTime":"2026-03-27T23:46:23Z","lastUpdateTime":"2026-03-27T23:46:23Z","message":"ReplicaSet \"trisla-portal-backend-5b65bf7898\" is progressing.","reason":"ReplicaSetUpdated","status":"True","type":"Progressing"}],"observedGeneration":138,"replicas":2,"unavailableReplicas":2,"updatedReplicas":1}}
      meta.helm.sh/release-name: trisla-portal
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-03-06T13:07:39Z"
    generation: 259
    labels:
      app: trisla-portal-backend
      app.kubernetes.io/managed-by: Helm
      component: backend
    name: trisla-portal-backend
    namespace: trisla
    resourceVersion: "886554101"
    uid: 0fd09586-cc4e-4938-8180-e8cbb3564a0f
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 2
    selector:
      matchLabels:
        app: trisla-portal-backend
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-07T22:18:48-03:00"
        creationTimestamp: null
        labels:
          app: trisla-portal-backend
          component: backend
      spec:
        containers:
        - command:
          - uvicorn
          - src.main:app
          - --host
          - 0.0.0.0
          - --port
          - "8888"
          - --workers
          - "1"
          env:
          - name: TRISLA_OBS_POLICY_DATASOURCE_SSOT_CM
            value: portal-datasources
          - name: TRISLA_OBS_POLICY_NO_REINSTRUMENTATION
            value: "true"
          - name: OBS_OTEL_COLLECTOR_HTTP
            value: http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318
          - name: OBS_OTEL_COLLECTOR_GRPC
            value: http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317
          - name: OBS_TEMPO_URL
            value: http://trisla-tempo.monitoring.svc.cluster.local:3200
          - name: OBS_JAEGER_URL
            value: http://trisla-jaeger.monitoring.svc.cluster.local:16686
          - name: OBS_GRAFANA_URL
            value: http://prometheus-grafana.monitoring.svc.cluster.local:80
          - name: OBS_PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: SEM_CSMF_URL
            value: http://trisla-sem-csmf:8080
          - name: ML_NSMF_URL
            value: http://trisla-ml-nsmf:8081
          - name: DECISION_ENGINE_URL
            value: http://trisla-decision-engine:8082
          - name: BC_NSSMF_URL
            value: http://trisla-bc-nssmf:8083
          - name: SLA_AGENT_URL
            value: http://trisla-sla-agent-layer:8084
          - name: OTEL_SDK_DISABLED
          - name: HTTP_TIMEOUT
            value: "30"
          - name: BC_TIMEOUT
            value: "60"
          - name: PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: TELEMETRY_PROMQL_RAN_LATENCY
            value: avg(trisla_ran_latency_ms{job="trisla-prb-simulator"})
          - name: TELEMETRY_PROMQL_TRANSPORT_RTT
            value: max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"})*1000
          - name: TELEMETRY_PROMQL_RAN_PRB
            value: avg(trisla_ran_prb_utilization)
          - name: TELEMETRY_PROMQL_TRANSPORT_JITTER
            value: avg((max_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m])
              - min_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]))
              * 1000)
          - name: SLA_AGENT_PIPELINE_INGEST_URL
            value: http://trisla-sla-agent-layer.trisla.svc.cluster.local:8084/api/v1/ingest/pipeline-event
          - name: USE_SLA_V2
            value: "true"
          - name: TELEMETRY_CORE_NAMESPACE
            value: ns-1274485
          - name: TELEMETRY_CORE_CPU_DENOM_MODE
            value: machine_cores
          - name: SLA_AGENT_REQUIRED_FOR_ACCEPT
            value: "true"
          image: ghcr.io/abelisboa/trisla-portal-backend@sha256:8435c4b5c6de1e3ccdc7d2b9721af6f360f4adcdc67f954bf64ad027181b1ea7
          imagePullPolicy: Always
          name: backend
          ports:
          - containerPort: 8888
            name: http
            protocol: TCP
          readinessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8888/health",timeout=3).read()
            failureThreshold: 5
            initialDelaySeconds: 15
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 256Mi
          startupProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8888/health",timeout=3).read()
            failureThreshold: 40
            initialDelaySeconds: 10
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 5
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        imagePullSecrets:
        - name: ghcr-secret
        nodeSelector:
          kubernetes.io/hostname: node1
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-07T14:47:22Z"
      lastUpdateTime: "2026-04-07T14:47:22Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-04-01T21:10:55Z"
      lastUpdateTime: "2026-04-13T01:54:53Z"
      message: ReplicaSet "trisla-portal-backend-5b6c77fbdb" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 259
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "9"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"trisla-portal-backend","app.kubernetes.io/managed-by":"Helm","component":"backend"},"name":"trisla-portal-backend-trisla","namespace":"trisla"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":2,"selector":{"matchLabels":{"app":"trisla-portal-backend-trisla"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt":"2026-04-07T22:18:48-03:00"},"creationTimestamp":null,"labels":{"app":"trisla-portal-backend-trisla","component":"backend"}},"spec":{"containers":[{"command":["uvicorn","src.main:app","--host","0.0.0.0","--port","8888","--workers","1"],"env":[{"name":"TRISLA_OBS_POLICY_DATASOURCE_SSOT_CM","value":"portal-datasources"},{"name":"TRISLA_OBS_POLICY_NO_REINSTRUMENTATION","value":"true"},{"name":"OBS_OTEL_COLLECTOR_HTTP","value":"http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318"},{"name":"OBS_OTEL_COLLECTOR_GRPC","value":"http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317"},{"name":"OBS_TEMPO_URL","value":"http://trisla-tempo.monitoring.svc.cluster.local:3200"},{"name":"OBS_JAEGER_URL","value":"http://trisla-jaeger.monitoring.svc.cluster.local:16686"},{"name":"OBS_GRAFANA_URL","value":"http://prometheus-grafana.monitoring.svc.cluster.local:80"},{"name":"OBS_PROMETHEUS_URL","value":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"},{"name":"SEM_CSMF_URL","value":"http://trisla-sem-csmf-trisla:8080"},{"name":"ML_NSMF_URL","value":"http://trisla-ml-nsmf:8081"},{"name":"DECISION_ENGINE_URL","value":"http://trisla-decision-engine:8082"},{"name":"BC_NSSMF_URL","value":"http://trisla-bc-nssmf:8083"},{"name":"SLA_AGENT_URL","value":"http://trisla-sla-agent-layer:8084"},{"name":"OTEL_SDK_DISABLED"},{"name":"HTTP_TIMEOUT","value":"30"},{"name":"BC_TIMEOUT","value":"60"},{"name":"PROMETHEUS_URL","value":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"},{"name":"TELEMETRY_PROMQL_RAN_LATENCY","value":"avg(trisla_ran_latency_ms{job=\"trisla-prb-simulator\"})"},{"name":"TELEMETRY_PROMQL_TRANSPORT_RTT","value":"max(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"})*1000"},{"name":"TELEMETRY_PROMQL_RAN_PRB","value":"avg(trisla_ran_prb_utilization{job!=\"trisla-prb-simulator\"})"},{"name":"TELEMETRY_PROMQL_TRANSPORT_JITTER","value":"avg((max_over_time(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"}[1m]) - min_over_time(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"}[1m])) * 1000)"},{"name":"SLA_AGENT_PIPELINE_INGEST_URL","value":"http://trisla-sla-agent-layer:8084/api/v1/ingest/pipeline-event"},{"name":"USE_SLA_V2","value":"true"},{"name":"TELEMETRY_CORE_NAMESPACE","value":"ns-1274485"},{"name":"TELEMETRY_CORE_CPU_DENOM_MODE","value":"machine_cores"},{"name":"POLICY_GOVERNED_MODE","value":"true"},{"name":"ML_ENABLED","value":"true"}],"image":"ghcr.io/abelisboa/trisla-portal-backend@sha256:2961a3eb7a90c96673f1789bc93502880f6a8bf47c50afd5fe7a6f0df1cbae7d","imagePullPolicy":"Always","name":"backend","ports":[{"containerPort":8888,"name":"http","protocol":"TCP"}],"readinessProbe":{"exec":{"command":["python3","-c","import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:8888/health\",timeout=3).read()"]},"failureThreshold":5,"initialDelaySeconds":15,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"256Mi"}},"startupProbe":{"exec":{"command":["python3","-c","import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:8888/health\",timeout=3).read()"]},"failureThreshold":40,"initialDelaySeconds":10,"periodSeconds":5,"successThreshold":1,"timeoutSeconds":5},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","imagePullSecrets":[{"name":"ghcr-secret"}],"nodeSelector":{"kubernetes.io/hostname":"node1"},"restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"terminationGracePeriodSeconds":30}}}}
    creationTimestamp: "2026-04-09T17:30:28Z"
    generation: 9
    labels:
      app: trisla-portal-backend
      app.kubernetes.io/managed-by: Helm
      component: backend
    name: trisla-portal-backend-trisla
    namespace: trisla
    resourceVersion: "886440827"
    uid: e4dc843e-601c-4b1f-b305-ac8071770f8e
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 2
    selector:
      matchLabels:
        app: trisla-portal-backend-trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-07T22:18:48-03:00"
        creationTimestamp: null
        labels:
          app: trisla-portal-backend-trisla
          component: backend
      spec:
        containers:
        - command:
          - uvicorn
          - src.main:app
          - --host
          - 0.0.0.0
          - --port
          - "8888"
          - --workers
          - "1"
          env:
          - name: TRISLA_OBS_POLICY_DATASOURCE_SSOT_CM
            value: portal-datasources
          - name: TRISLA_OBS_POLICY_NO_REINSTRUMENTATION
            value: "true"
          - name: OBS_OTEL_COLLECTOR_HTTP
            value: http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318
          - name: OBS_OTEL_COLLECTOR_GRPC
            value: http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317
          - name: OBS_TEMPO_URL
            value: http://trisla-tempo.monitoring.svc.cluster.local:3200
          - name: OBS_JAEGER_URL
            value: http://trisla-jaeger.monitoring.svc.cluster.local:16686
          - name: OBS_GRAFANA_URL
            value: http://prometheus-grafana.monitoring.svc.cluster.local:80
          - name: OBS_PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: ML_NSMF_URL
            value: http://trisla-ml-nsmf:8081
          - name: DECISION_ENGINE_URL
            value: http://trisla-decision-engine:8082
          - name: BC_NSSMF_URL
            value: http://trisla-bc-nssmf:8083
          - name: SLA_AGENT_URL
            value: http://trisla-sla-agent-layer:8084
          - name: OTEL_SDK_DISABLED
          - name: HTTP_TIMEOUT
            value: "30"
          - name: BC_TIMEOUT
            value: "60"
          - name: PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: TELEMETRY_PROMQL_RAN_LATENCY
            value: avg(trisla_ran_latency_ms{job="trisla-prb-simulator"})
          - name: TELEMETRY_PROMQL_TRANSPORT_RTT
            value: max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"})*1000
          - name: TELEMETRY_PROMQL_RAN_PRB
            value: avg(trisla_ran_prb_utilization{job="trisla-prb-simulator"})
          - name: TELEMETRY_PROMQL_TRANSPORT_JITTER
            value: avg((max_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m])
              - min_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]))
              * 1000)
          - name: SLA_AGENT_PIPELINE_INGEST_URL
            value: http://trisla-sla-agent-layer:8084/api/v1/ingest/pipeline-event
          - name: USE_SLA_V2
            value: "true"
          - name: TELEMETRY_CORE_NAMESPACE
            value: ns-1274485
          - name: TELEMETRY_CORE_CPU_DENOM_MODE
            value: machine_cores
          - name: POLICY_GOVERNED_MODE
            value: "true"
          - name: ML_ENABLED
            value: "true"
          image: ghcr.io/abelisboa/trisla-portal-backend@sha256:2961a3eb7a90c96673f1789bc93502880f6a8bf47c50afd5fe7a6f0df1cbae7d
          imagePullPolicy: Always
          name: backend
          ports:
          - containerPort: 8888
            name: http
            protocol: TCP
          readinessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8888/health",timeout=3).read()
            failureThreshold: 5
            initialDelaySeconds: 15
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 256Mi
          startupProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8888/health",timeout=3).read()
            failureThreshold: 40
            initialDelaySeconds: 10
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 5
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        imagePullSecrets:
        - name: ghcr-secret
        nodeSelector:
          kubernetes.io/hostname: node1
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-09T17:30:49Z"
      lastUpdateTime: "2026-04-09T17:30:49Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-04-09T17:30:28Z"
      lastUpdateTime: "2026-04-12T15:41:11Z"
      message: ReplicaSet "trisla-portal-backend-trisla-9f8d89bf9" has successfully
        progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 9
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "4"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"trisla-portal-backend","app.kubernetes.io/managed-by":"Helm","component":"backend"},"name":"trisla-portal-backend-v1","namespace":"trisla"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":2,"selector":{"matchLabels":{"app":"trisla-portal-backend-v1"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt":"2026-04-07T22:18:48-03:00"},"creationTimestamp":null,"labels":{"app":"trisla-portal-backend-v1","component":"backend"}},"spec":{"containers":[{"command":["uvicorn","src.main:app","--host","0.0.0.0","--port","8888","--workers","1"],"env":[{"name":"TRISLA_OBS_POLICY_DATASOURCE_SSOT_CM","value":"portal-datasources"},{"name":"TRISLA_OBS_POLICY_NO_REINSTRUMENTATION","value":"true"},{"name":"OBS_OTEL_COLLECTOR_HTTP","value":"http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318"},{"name":"OBS_OTEL_COLLECTOR_GRPC","value":"http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317"},{"name":"OBS_TEMPO_URL","value":"http://trisla-tempo.monitoring.svc.cluster.local:3200"},{"name":"OBS_JAEGER_URL","value":"http://trisla-jaeger.monitoring.svc.cluster.local:16686"},{"name":"OBS_GRAFANA_URL","value":"http://prometheus-grafana.monitoring.svc.cluster.local:80"},{"name":"OBS_PROMETHEUS_URL","value":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"},{"name":"SEM_CSMF_URL","value":"http://trisla-sem-csmf-v1:8080"},{"name":"ML_NSMF_URL","value":"http://trisla-ml-nsmf:8081"},{"name":"DECISION_ENGINE_URL","value":"http://trisla-decision-engine:8082"},{"name":"BC_NSSMF_URL","value":"http://trisla-bc-nssmf:8083"},{"name":"SLA_AGENT_URL","value":"http://trisla-sla-agent-layer:8084"},{"name":"OTEL_SDK_DISABLED"},{"name":"HTTP_TIMEOUT","value":"30"},{"name":"BC_TIMEOUT","value":"60"},{"name":"PROMETHEUS_URL","value":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"},{"name":"TELEMETRY_PROMQL_RAN_LATENCY","value":"avg(trisla_ran_latency_ms{job=\"trisla-prb-simulator\"})"},{"name":"TELEMETRY_PROMQL_TRANSPORT_RTT","value":"max(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"})*1000"},{"name":"TELEMETRY_PROMQL_RAN_PRB","value":"avg(trisla_ran_prb_utilization{job!=\"trisla-prb-simulator\"})"},{"name":"TELEMETRY_PROMQL_TRANSPORT_JITTER","value":"avg((max_over_time(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"}[1m]) - min_over_time(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"}[1m])) * 1000)"},{"name":"SLA_AGENT_PIPELINE_INGEST_URL","value":"http://trisla-sla-agent-layer:8084/api/v1/ingest/pipeline-event"},{"name":"USE_SLA_V2","value":"false"},{"name":"TELEMETRY_CORE_NAMESPACE","value":"ns-1274485"},{"name":"TELEMETRY_CORE_CPU_DENOM_MODE","value":"machine_cores"},{"name":"POLICY_GOVERNED_MODE","value":"false"},{"name":"ML_ENABLED","value":"false"}],"image":"ghcr.io/abelisboa/trisla-portal-backend@sha256:2961a3eb7a90c96673f1789bc93502880f6a8bf47c50afd5fe7a6f0df1cbae7d","imagePullPolicy":"Always","name":"backend","ports":[{"containerPort":8888,"name":"http","protocol":"TCP"}],"readinessProbe":{"exec":{"command":["python3","-c","import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:8888/health\",timeout=3).read()"]},"failureThreshold":5,"initialDelaySeconds":15,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"256Mi"}},"startupProbe":{"exec":{"command":["python3","-c","import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:8888/health\",timeout=3).read()"]},"failureThreshold":40,"initialDelaySeconds":10,"periodSeconds":5,"successThreshold":1,"timeoutSeconds":5},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","imagePullSecrets":[{"name":"ghcr-secret"}],"nodeSelector":{"kubernetes.io/hostname":"node1"},"restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"terminationGracePeriodSeconds":30}}}}
    creationTimestamp: "2026-04-09T17:30:28Z"
    generation: 4
    labels:
      app: trisla-portal-backend
      app.kubernetes.io/managed-by: Helm
      component: backend
    name: trisla-portal-backend-v1
    namespace: trisla
    resourceVersion: "885705364"
    uid: 99a87c80-4428-4cb5-8944-a503bbfbd82a
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 2
    selector:
      matchLabels:
        app: trisla-portal-backend-v1
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-07T22:18:48-03:00"
        creationTimestamp: null
        labels:
          app: trisla-portal-backend-v1
          component: backend
      spec:
        containers:
        - command:
          - uvicorn
          - src.main:app
          - --host
          - 0.0.0.0
          - --port
          - "8888"
          - --workers
          - "1"
          env:
          - name: TRISLA_OBS_POLICY_DATASOURCE_SSOT_CM
            value: portal-datasources
          - name: TRISLA_OBS_POLICY_NO_REINSTRUMENTATION
            value: "true"
          - name: OBS_OTEL_COLLECTOR_HTTP
            value: http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318
          - name: OBS_OTEL_COLLECTOR_GRPC
            value: http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317
          - name: OBS_TEMPO_URL
            value: http://trisla-tempo.monitoring.svc.cluster.local:3200
          - name: OBS_JAEGER_URL
            value: http://trisla-jaeger.monitoring.svc.cluster.local:16686
          - name: OBS_GRAFANA_URL
            value: http://prometheus-grafana.monitoring.svc.cluster.local:80
          - name: OBS_PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: ML_NSMF_URL
            value: http://trisla-ml-nsmf:8081
          - name: DECISION_ENGINE_URL
            value: http://trisla-decision-engine:8082
          - name: BC_NSSMF_URL
            value: http://trisla-bc-nssmf:8083
          - name: SLA_AGENT_URL
            value: http://trisla-sla-agent-layer:8084
          - name: OTEL_SDK_DISABLED
          - name: HTTP_TIMEOUT
            value: "30"
          - name: BC_TIMEOUT
            value: "60"
          - name: PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: TELEMETRY_PROMQL_RAN_LATENCY
            value: avg(trisla_ran_latency_ms{job="trisla-prb-simulator"})
          - name: TELEMETRY_PROMQL_TRANSPORT_RTT
            value: max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"})*1000
          - name: TELEMETRY_PROMQL_RAN_PRB
            value: avg(trisla_ran_prb_utilization{job!="trisla-prb-simulator"})
          - name: TELEMETRY_PROMQL_TRANSPORT_JITTER
            value: avg((max_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m])
              - min_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]))
              * 1000)
          - name: SLA_AGENT_PIPELINE_INGEST_URL
            value: http://trisla-sla-agent-layer:8084/api/v1/ingest/pipeline-event
          - name: USE_SLA_V2
            value: "false"
          - name: TELEMETRY_CORE_NAMESPACE
            value: ns-1274485
          - name: TELEMETRY_CORE_CPU_DENOM_MODE
            value: machine_cores
          - name: POLICY_GOVERNED_MODE
            value: "false"
          - name: ML_ENABLED
            value: "false"
          image: ghcr.io/abelisboa/trisla-portal-backend@sha256:2961a3eb7a90c96673f1789bc93502880f6a8bf47c50afd5fe7a6f0df1cbae7d
          imagePullPolicy: Always
          name: backend
          ports:
          - containerPort: 8888
            name: http
            protocol: TCP
          readinessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8888/health",timeout=3).read()
            failureThreshold: 5
            initialDelaySeconds: 15
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 256Mi
          startupProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8888/health",timeout=3).read()
            failureThreshold: 40
            initialDelaySeconds: 10
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 5
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        imagePullSecrets:
        - name: ghcr-secret
        nodeSelector:
          kubernetes.io/hostname: node1
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-09T17:30:49Z"
      lastUpdateTime: "2026-04-09T17:30:49Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-04-09T17:30:28Z"
      lastUpdateTime: "2026-04-09T18:17:52Z"
      message: ReplicaSet "trisla-portal-backend-v1-5886d844c7" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 4
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "4"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"trisla-portal-backend","app.kubernetes.io/managed-by":"Helm","component":"backend"},"name":"trisla-portal-backend-v2","namespace":"trisla"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":2,"selector":{"matchLabels":{"app":"trisla-portal-backend-v2"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt":"2026-04-07T22:18:48-03:00"},"creationTimestamp":null,"labels":{"app":"trisla-portal-backend-v2","component":"backend"}},"spec":{"containers":[{"command":["uvicorn","src.main:app","--host","0.0.0.0","--port","8888","--workers","1"],"env":[{"name":"TRISLA_OBS_POLICY_DATASOURCE_SSOT_CM","value":"portal-datasources"},{"name":"TRISLA_OBS_POLICY_NO_REINSTRUMENTATION","value":"true"},{"name":"OBS_OTEL_COLLECTOR_HTTP","value":"http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318"},{"name":"OBS_OTEL_COLLECTOR_GRPC","value":"http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317"},{"name":"OBS_TEMPO_URL","value":"http://trisla-tempo.monitoring.svc.cluster.local:3200"},{"name":"OBS_JAEGER_URL","value":"http://trisla-jaeger.monitoring.svc.cluster.local:16686"},{"name":"OBS_GRAFANA_URL","value":"http://prometheus-grafana.monitoring.svc.cluster.local:80"},{"name":"OBS_PROMETHEUS_URL","value":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"},{"name":"SEM_CSMF_URL","value":"http://trisla-sem-csmf-v2:8080"},{"name":"ML_NSMF_URL","value":"http://trisla-ml-nsmf:8081"},{"name":"DECISION_ENGINE_URL","value":"http://trisla-decision-engine:8082"},{"name":"BC_NSSMF_URL","value":"http://trisla-bc-nssmf:8083"},{"name":"SLA_AGENT_URL","value":"http://trisla-sla-agent-layer:8084"},{"name":"OTEL_SDK_DISABLED"},{"name":"HTTP_TIMEOUT","value":"30"},{"name":"BC_TIMEOUT","value":"60"},{"name":"PROMETHEUS_URL","value":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"},{"name":"TELEMETRY_PROMQL_RAN_LATENCY","value":"avg(trisla_ran_latency_ms{job=\"trisla-prb-simulator\"})"},{"name":"TELEMETRY_PROMQL_TRANSPORT_RTT","value":"max(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"})*1000"},{"name":"TELEMETRY_PROMQL_RAN_PRB","value":"avg(trisla_ran_prb_utilization{job!=\"trisla-prb-simulator\"})"},{"name":"TELEMETRY_PROMQL_TRANSPORT_JITTER","value":"avg((max_over_time(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"}[1m]) - min_over_time(probe_duration_seconds{job=\"probe/monitoring/trisla-transport-tcp-probe\"}[1m])) * 1000)"},{"name":"SLA_AGENT_PIPELINE_INGEST_URL","value":"http://trisla-sla-agent-layer:8084/api/v1/ingest/pipeline-event"},{"name":"USE_SLA_V2","value":"true"},{"name":"TELEMETRY_CORE_NAMESPACE","value":"ns-1274485"},{"name":"TELEMETRY_CORE_CPU_DENOM_MODE","value":"machine_cores"},{"name":"POLICY_GOVERNED_MODE","value":"false"},{"name":"ML_ENABLED","value":"true"}],"image":"ghcr.io/abelisboa/trisla-portal-backend@sha256:2961a3eb7a90c96673f1789bc93502880f6a8bf47c50afd5fe7a6f0df1cbae7d","imagePullPolicy":"Always","name":"backend","ports":[{"containerPort":8888,"name":"http","protocol":"TCP"}],"readinessProbe":{"exec":{"command":["python3","-c","import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:8888/health\",timeout=3).read()"]},"failureThreshold":5,"initialDelaySeconds":15,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"256Mi"}},"startupProbe":{"exec":{"command":["python3","-c","import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:8888/health\",timeout=3).read()"]},"failureThreshold":40,"initialDelaySeconds":10,"periodSeconds":5,"successThreshold":1,"timeoutSeconds":5},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","imagePullSecrets":[{"name":"ghcr-secret"}],"nodeSelector":{"kubernetes.io/hostname":"node1"},"restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"terminationGracePeriodSeconds":30}}}}
    creationTimestamp: "2026-04-09T17:30:28Z"
    generation: 4
    labels:
      app: trisla-portal-backend
      app.kubernetes.io/managed-by: Helm
      component: backend
    name: trisla-portal-backend-v2
    namespace: trisla
    resourceVersion: "885705381"
    uid: 2a3d2942-b934-49a0-b83d-ce2080f8a596
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 2
    selector:
      matchLabels:
        app: trisla-portal-backend-v2
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-07T22:18:48-03:00"
        creationTimestamp: null
        labels:
          app: trisla-portal-backend-v2
          component: backend
      spec:
        containers:
        - command:
          - uvicorn
          - src.main:app
          - --host
          - 0.0.0.0
          - --port
          - "8888"
          - --workers
          - "1"
          env:
          - name: TRISLA_OBS_POLICY_DATASOURCE_SSOT_CM
            value: portal-datasources
          - name: TRISLA_OBS_POLICY_NO_REINSTRUMENTATION
            value: "true"
          - name: OBS_OTEL_COLLECTOR_HTTP
            value: http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318
          - name: OBS_OTEL_COLLECTOR_GRPC
            value: http://trisla-otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317
          - name: OBS_TEMPO_URL
            value: http://trisla-tempo.monitoring.svc.cluster.local:3200
          - name: OBS_JAEGER_URL
            value: http://trisla-jaeger.monitoring.svc.cluster.local:16686
          - name: OBS_GRAFANA_URL
            value: http://prometheus-grafana.monitoring.svc.cluster.local:80
          - name: OBS_PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: ML_NSMF_URL
            value: http://trisla-ml-nsmf:8081
          - name: DECISION_ENGINE_URL
            value: http://trisla-decision-engine:8082
          - name: BC_NSSMF_URL
            value: http://trisla-bc-nssmf:8083
          - name: SLA_AGENT_URL
            value: http://trisla-sla-agent-layer:8084
          - name: OTEL_SDK_DISABLED
          - name: HTTP_TIMEOUT
            value: "30"
          - name: BC_TIMEOUT
            value: "60"
          - name: PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: TELEMETRY_PROMQL_RAN_LATENCY
            value: avg(trisla_ran_latency_ms{job="trisla-prb-simulator"})
          - name: TELEMETRY_PROMQL_TRANSPORT_RTT
            value: max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"})*1000
          - name: TELEMETRY_PROMQL_RAN_PRB
            value: avg(trisla_ran_prb_utilization{job!="trisla-prb-simulator"})
          - name: TELEMETRY_PROMQL_TRANSPORT_JITTER
            value: avg((max_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m])
              - min_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]))
              * 1000)
          - name: SLA_AGENT_PIPELINE_INGEST_URL
            value: http://trisla-sla-agent-layer:8084/api/v1/ingest/pipeline-event
          - name: USE_SLA_V2
            value: "true"
          - name: TELEMETRY_CORE_NAMESPACE
            value: ns-1274485
          - name: TELEMETRY_CORE_CPU_DENOM_MODE
            value: machine_cores
          - name: POLICY_GOVERNED_MODE
            value: "false"
          - name: ML_ENABLED
            value: "true"
          image: ghcr.io/abelisboa/trisla-portal-backend@sha256:2961a3eb7a90c96673f1789bc93502880f6a8bf47c50afd5fe7a6f0df1cbae7d
          imagePullPolicy: Always
          name: backend
          ports:
          - containerPort: 8888
            name: http
            protocol: TCP
          readinessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8888/health",timeout=3).read()
            failureThreshold: 5
            initialDelaySeconds: 15
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 256Mi
          startupProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8888/health",timeout=3).read()
            failureThreshold: 40
            initialDelaySeconds: 10
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 5
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        imagePullSecrets:
        - name: ghcr-secret
        nodeSelector:
          kubernetes.io/hostname: node1
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-09T17:30:49Z"
      lastUpdateTime: "2026-04-09T17:30:49Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-04-09T17:30:28Z"
      lastUpdateTime: "2026-04-09T18:17:52Z"
      message: ReplicaSet "trisla-portal-backend-v2-5b9466875b" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 4
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "24"
      meta.helm.sh/release-name: trisla-portal
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-03-17T18:39:21Z"
    generation: 24
    labels:
      app: trisla-portal-frontend
      app.kubernetes.io/managed-by: Helm
      component: frontend
    name: trisla-portal-frontend
    namespace: trisla
    resourceVersion: "886497382"
    uid: 10c4ecc4-9708-4756-92b6-051008903492
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-portal-frontend
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        creationTimestamp: null
        labels:
          app: trisla-portal-frontend
          component: frontend
      spec:
        containers:
        - env:
          - name: BACKEND_URL
            value: /api
          - name: API_BACKEND_URL
            value: http://trisla-portal-backend:8001
          image: ghcr.io/abelisboa/trisla-portal-frontend@sha256:1a1b82fc1e5b97cf1b4617354e5ac709507b5934864aea71fe2e84e8239d4d2f
          imagePullPolicy: Always
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /
              port: 3000
              scheme: HTTP
            initialDelaySeconds: 30
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          name: frontend
          ports:
          - containerPort: 3000
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /
              port: 3000
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 3
          resources:
            limits:
              cpu: 200m
              memory: 256Mi
            requests:
              cpu: 50m
              memory: 128Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-18T23:22:03Z"
      lastUpdateTime: "2026-03-19T00:24:38Z"
      message: ReplicaSet "trisla-portal-frontend-78ccbcbfdd" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:02:55Z"
      lastUpdateTime: "2026-04-12T21:02:55Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 24
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "6"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"trisla-prb-simulator","app.kubernetes.io/name":"trisla-prb-simulator"},"name":"trisla-prb-simulator","namespace":"trisla"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"trisla-prb-simulator"}},"template":{"metadata":{"labels":{"app":"trisla-prb-simulator","app.kubernetes.io/name":"trisla-prb-simulator"}},"spec":{"containers":[{"args":["pip install --no-cache-dir fastapi==0.109.0 uvicorn[standard]==0.27.0 prometheus-client==0.19.0 \u0026\u0026 uvicorn main:app --host 0.0.0.0 --port 8086"],"command":["/bin/sh","-lc"],"env":[{"name":"PRB_SCENARIO","value":"scenario_1"}],"image":"python:3.10-slim","imagePullPolicy":"IfNotPresent","name":"prb-simulator","ports":[{"containerPort":8086,"name":"http"}],"volumeMounts":[{"mountPath":"/main.py","name":"app-code","subPath":"main.py"}]}],"volumes":[{"configMap":{"name":"trisla-prb-simulator-code"},"name":"app-code"}]}}}}
    creationTimestamp: "2026-03-23T14:58:23Z"
    generation: 10
    labels:
      app: trisla-prb-simulator
      app.kubernetes.io/name: trisla-prb-simulator
    name: trisla-prb-simulator
    namespace: trisla
    resourceVersion: "886023227"
    uid: 3e305ab3-9b82-403a-a865-fe921ca0d1d0
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-prb-simulator
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-01T18:47:08-03:00"
        creationTimestamp: null
        labels:
          app: trisla-prb-simulator
          app.kubernetes.io/name: trisla-prb-simulator
      spec:
        containers:
        - args:
          - pip install --no-cache-dir fastapi==0.109.0 uvicorn[standard]==0.27.0
            prometheus-client==0.19.0 && uvicorn main:app --host 0.0.0.0 --port 8086
          command:
          - /bin/sh
          - -lc
          env:
          - name: PRB_SCENARIO
            value: scenario_1
          image: python:3.10-slim
          imagePullPolicy: IfNotPresent
          name: prb-simulator
          ports:
          - containerPort: 8086
            name: http
            protocol: TCP
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          volumeMounts:
          - mountPath: /main.py
            name: app-code
            subPath: main.py
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
        volumes:
        - configMap:
            defaultMode: 420
            name: trisla-prb-simulator-code
          name: app-code
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-23T14:58:23Z"
      lastUpdateTime: "2026-04-01T21:47:10Z"
      message: ReplicaSet "trisla-prb-simulator-cf8654758" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-11T00:58:23Z"
      lastUpdateTime: "2026-04-11T00:58:23Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 10
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "3"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"trisla-ran-ue-upf-proxy"},"name":"trisla-ran-ue-upf-proxy","namespace":"trisla"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"trisla-ran-ue-upf-proxy"}},"template":{"metadata":{"labels":{"app":"trisla-ran-ue-upf-proxy"}},"spec":{"containers":[{"args":["pip install --no-cache-dir flask==3.0.0 requests==2.31.0 gunicorn==21.2.0\nexec gunicorn -b 0.0.0.0:9102 --workers 1 --threads 2 exporter:app\n"],"command":["/bin/sh","-c"],"env":[{"name":"PROMETHEUS_URL","value":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"},{"name":"RAN_PROXY_NAMESPACE","value":"ns-1274485"},{"name":"RAN_PROXY_UPF_POD_REGEX","value":"upf.*"},{"name":"RAN_PROXY_UE_POD_REGEX","value":"no-such-ue"},{"name":"RAN_PROXY_RATE_WINDOW","value":"2m"},{"name":"RAN_PROXY_MAX_THROUGHPUT_BPS","value":"200000000"},{"name":"RAN_PROXY_PROM_TIMEOUT","value":"10"}],"image":"docker.io/library/python:3.11-slim","imagePullPolicy":"IfNotPresent","livenessProbe":{"httpGet":{"path":"/healthz","port":9102},"initialDelaySeconds":90,"periodSeconds":30},"name":"exporter","ports":[{"containerPort":9102,"name":"metrics"}],"readinessProbe":{"httpGet":{"path":"/healthz","port":9102},"initialDelaySeconds":45,"periodSeconds":10},"volumeMounts":[{"mountPath":"/app","name":"code","readOnly":true}],"workingDir":"/app"}],"volumes":[{"configMap":{"name":"trisla-ran-ue-upf-proxy-code"},"name":"code"}]}}}}
    creationTimestamp: "2026-04-11T00:51:12Z"
    generation: 3
    labels:
      app: trisla-ran-ue-upf-proxy
    name: trisla-ran-ue-upf-proxy
    namespace: trisla
    resourceVersion: "886022121"
    uid: 4e1b0c00-5541-4e0b-b275-8b1853d0144c
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-ran-ue-upf-proxy
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-10T21:54:37-03:00"
        creationTimestamp: null
        labels:
          app: trisla-ran-ue-upf-proxy
      spec:
        containers:
        - args:
          - |
            pip install --no-cache-dir flask==3.0.0 requests==2.31.0 gunicorn==21.2.0
            exec gunicorn -b 0.0.0.0:9102 --workers 1 --threads 2 exporter:app
          command:
          - /bin/sh
          - -c
          env:
          - name: PROMETHEUS_URL
            value: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          - name: RAN_PROXY_NAMESPACE
            value: ns-1274485
          - name: RAN_PROXY_UPF_POD_REGEX
            value: upf.*
          - name: RAN_PROXY_UE_POD_REGEX
            value: no-such-ue
          - name: RAN_PROXY_RATE_WINDOW
            value: 2m
          - name: RAN_PROXY_MAX_THROUGHPUT_BPS
            value: "200000000"
          - name: RAN_PROXY_PROM_TIMEOUT
            value: "10"
          image: docker.io/library/python:3.11-slim
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /healthz
              port: 9102
              scheme: HTTP
            initialDelaySeconds: 90
            periodSeconds: 30
            successThreshold: 1
            timeoutSeconds: 1
          name: exporter
          ports:
          - containerPort: 9102
            name: metrics
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /healthz
              port: 9102
              scheme: HTTP
            initialDelaySeconds: 45
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          volumeMounts:
          - mountPath: /app
            name: code
            readOnly: true
          workingDir: /app
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
        volumes:
        - configMap:
            defaultMode: 420
            name: trisla-ran-ue-upf-proxy-code
          name: code
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-11T00:52:51Z"
      lastUpdateTime: "2026-04-11T00:52:51Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-04-11T00:51:12Z"
      lastUpdateTime: "2026-04-11T00:52:51Z"
      message: ReplicaSet "trisla-ran-ue-upf-proxy-db48f9b54" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 3
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "78"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-02-14T21:18:35Z"
    generation: 80
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-sem-csmf
    namespace: trisla
    resourceVersion: "886554186"
    uid: c41ba896-ebb8-4103-9667-25e83a6fca17
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-sem-csmf
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-05T22:48:50-03:00"
        creationTimestamp: null
        labels:
          app: trisla-sem-csmf
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: KAFKA_ENABLED
            value: "true"
          - name: KAFKA_BROKERS
            value: kafka:9092
          - name: SEM_PRB_JOB_PRIORITY
            value: trisla-ran-ue-upf-proxy
          image: ghcr.io/abelisboa/trisla-sem-csmf@sha256:5e7252a4285b243fe2ac483fb235d393c51141c9970a68cbf1ff8a666b4f3ec3
          imagePullPolicy: IfNotPresent
          livenessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/health",
                timeout=5).read()
            failureThreshold: 5
            initialDelaySeconds: 60
            periodSeconds: 15
            successThreshold: 1
            timeoutSeconds: 6
          name: sem-csmf
          ports:
          - containerPort: 8080
            name: http
            protocol: TCP
          readinessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/health",
                timeout=5).read()
            failureThreshold: 5
            initialDelaySeconds: 30
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 6
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        imagePullSecrets:
        - name: ghcr-secret
        nodeSelector:
          kubernetes.io/hostname: node1
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-06T01:46:23Z"
      lastUpdateTime: "2026-04-06T01:46:23Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    - lastTransitionTime: "2026-03-31T20:13:09Z"
      lastUpdateTime: "2026-04-13T01:55:13Z"
      message: ReplicaSet "trisla-sem-csmf-65cb46f8d9" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    observedGeneration: 80
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "3"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"trisla","app.kubernetes.io/managed-by":"Helm","app.kubernetes.io/name":"trisla","helm.sh/chart":"trisla-3.10.0"},"name":"trisla-sem-csmf-trisla","namespace":"trisla"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":10,"selector":{"matchLabels":{"app":"trisla-sem-csmf-trisla","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt":"2026-04-05T22:48:50-03:00"},"creationTimestamp":null,"labels":{"app":"trisla-sem-csmf-trisla","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"spec":{"containers":[{"env":[{"name":"TRISLA_NODE_INTERFACE","value":"my5g"},{"name":"TRISLA_NODE_IP","value":"192.168.10.16"},{"name":"OTLP_ENDPOINT","value":"http://trisla-otel-collector:4317"},{"name":"KAFKA_ENABLED","value":"true"},{"name":"KAFKA_BROKERS","value":"kafka:9092"},{"name":"DECISION_ENGINE_URL","value":"http://trisla-decision-engine-trisla:8082/evaluate"}],"image":"ghcr.io/abelisboa/trisla-sem-csmf@sha256:31f32c78db0c07165c5ac6fa0f2b46af75fcfc5162a214d23ef0bd18f577f541","imagePullPolicy":"IfNotPresent","livenessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":30,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":1},"name":"sem-csmf","ports":[{"containerPort":8080,"name":"http","protocol":"TCP"}],"readinessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":10,"periodSeconds":5,"successThreshold":1,"timeoutSeconds":1},"resources":{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"500m","memory":"512Mi"}},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","imagePullSecrets":[{"name":"ghcr-secret"}],"nodeSelector":{"kubernetes.io/hostname":"node2"},"restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"terminationGracePeriodSeconds":30}}}}
    creationTimestamp: "2026-04-09T17:30:28Z"
    generation: 3
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-sem-csmf-trisla
    namespace: trisla
    resourceVersion: "886497635"
    uid: 1f814449-841e-47a8-9faf-3cd430c528ae
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-sem-csmf-trisla
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-05T22:48:50-03:00"
        creationTimestamp: null
        labels:
          app: trisla-sem-csmf-trisla
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: KAFKA_ENABLED
            value: "true"
          - name: KAFKA_BROKERS
            value: kafka:9092
          - name: DECISION_ENGINE_URL
            value: http://trisla-decision-engine-trisla:8082/evaluate
          - name: SEM_PRB_JOB_PRIORITY
            value: trisla-prb-simulator,trisla-ran-ue-upf-proxy
          image: ghcr.io/abelisboa/trisla-sem-csmf@sha256:31f32c78db0c07165c5ac6fa0f2b46af75fcfc5162a214d23ef0bd18f577f541
          imagePullPolicy: IfNotPresent
          livenessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/health",
                timeout=5).read()
            failureThreshold: 5
            initialDelaySeconds: 60
            periodSeconds: 15
            successThreshold: 1
            timeoutSeconds: 6
          name: sem-csmf
          ports:
          - containerPort: 8080
            name: http
            protocol: TCP
          readinessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/health",
                timeout=5).read()
            failureThreshold: 5
            initialDelaySeconds: 30
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 6
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        imagePullSecrets:
        - name: ghcr-secret
        nodeSelector:
          kubernetes.io/hostname: node2
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-09T17:30:28Z"
      lastUpdateTime: "2026-04-12T15:30:18Z"
      message: ReplicaSet "trisla-sem-csmf-trisla-78bb86b6fd" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:03:24Z"
      lastUpdateTime: "2026-04-12T21:03:24Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 3
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "2"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"trisla","app.kubernetes.io/managed-by":"Helm","app.kubernetes.io/name":"trisla","helm.sh/chart":"trisla-3.10.0"},"name":"trisla-sem-csmf-v1","namespace":"trisla"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":10,"selector":{"matchLabels":{"app":"trisla-sem-csmf-v1","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt":"2026-04-05T22:48:50-03:00"},"creationTimestamp":null,"labels":{"app":"trisla-sem-csmf-v1","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"spec":{"containers":[{"env":[{"name":"TRISLA_NODE_INTERFACE","value":"my5g"},{"name":"TRISLA_NODE_IP","value":"192.168.10.16"},{"name":"OTLP_ENDPOINT","value":"http://trisla-otel-collector:4317"},{"name":"KAFKA_ENABLED","value":"true"},{"name":"KAFKA_BROKERS","value":"kafka:9092"},{"name":"DECISION_ENGINE_URL","value":"http://trisla-decision-engine-v1:8082/evaluate"}],"image":"ghcr.io/abelisboa/trisla-sem-csmf@sha256:31f32c78db0c07165c5ac6fa0f2b46af75fcfc5162a214d23ef0bd18f577f541","imagePullPolicy":"IfNotPresent","livenessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":30,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":1},"name":"sem-csmf","ports":[{"containerPort":8080,"name":"http","protocol":"TCP"}],"readinessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":10,"periodSeconds":5,"successThreshold":1,"timeoutSeconds":1},"resources":{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"500m","memory":"512Mi"}},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","imagePullSecrets":[{"name":"ghcr-secret"}],"nodeSelector":{"kubernetes.io/hostname":"node2"},"restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"terminationGracePeriodSeconds":30}}}}
    creationTimestamp: "2026-04-09T17:30:28Z"
    generation: 2
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-sem-csmf-v1
    namespace: trisla
    resourceVersion: "886497617"
    uid: bf4700f6-788b-4729-8887-7777c79aca78
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-sem-csmf-v1
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-05T22:48:50-03:00"
        creationTimestamp: null
        labels:
          app: trisla-sem-csmf-v1
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: KAFKA_ENABLED
            value: "true"
          - name: KAFKA_BROKERS
            value: kafka:9092
          - name: DECISION_ENGINE_URL
            value: http://trisla-decision-engine-v1:8082/evaluate
          image: ghcr.io/abelisboa/trisla-sem-csmf@sha256:31f32c78db0c07165c5ac6fa0f2b46af75fcfc5162a214d23ef0bd18f577f541
          imagePullPolicy: IfNotPresent
          livenessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/health",
                timeout=5).read()
            failureThreshold: 5
            initialDelaySeconds: 60
            periodSeconds: 15
            successThreshold: 1
            timeoutSeconds: 6
          name: sem-csmf
          ports:
          - containerPort: 8080
            name: http
            protocol: TCP
          readinessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/health",
                timeout=5).read()
            failureThreshold: 5
            initialDelaySeconds: 30
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 6
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        imagePullSecrets:
        - name: ghcr-secret
        nodeSelector:
          kubernetes.io/hostname: node2
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-09T17:30:28Z"
      lastUpdateTime: "2026-04-09T17:37:38Z"
      message: ReplicaSet "trisla-sem-csmf-v1-584c8cc86b" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:03:24Z"
      lastUpdateTime: "2026-04-12T21:03:24Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 2
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "2"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"trisla","app.kubernetes.io/managed-by":"Helm","app.kubernetes.io/name":"trisla","helm.sh/chart":"trisla-3.10.0"},"name":"trisla-sem-csmf-v2","namespace":"trisla"},"spec":{"progressDeadlineSeconds":600,"replicas":1,"revisionHistoryLimit":10,"selector":{"matchLabels":{"app":"trisla-sem-csmf-v2","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"strategy":{"rollingUpdate":{"maxSurge":"25%","maxUnavailable":"25%"},"type":"RollingUpdate"},"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt":"2026-04-05T22:48:50-03:00"},"creationTimestamp":null,"labels":{"app":"trisla-sem-csmf-v2","app.kubernetes.io/instance":"trisla","app.kubernetes.io/name":"trisla"}},"spec":{"containers":[{"env":[{"name":"TRISLA_NODE_INTERFACE","value":"my5g"},{"name":"TRISLA_NODE_IP","value":"192.168.10.16"},{"name":"OTLP_ENDPOINT","value":"http://trisla-otel-collector:4317"},{"name":"KAFKA_ENABLED","value":"true"},{"name":"KAFKA_BROKERS","value":"kafka:9092"},{"name":"DECISION_ENGINE_URL","value":"http://trisla-decision-engine-v2:8082/evaluate"}],"image":"ghcr.io/abelisboa/trisla-sem-csmf@sha256:31f32c78db0c07165c5ac6fa0f2b46af75fcfc5162a214d23ef0bd18f577f541","imagePullPolicy":"IfNotPresent","livenessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":30,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":1},"name":"sem-csmf","ports":[{"containerPort":8080,"name":"http","protocol":"TCP"}],"readinessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":"http","scheme":"HTTP"},"initialDelaySeconds":10,"periodSeconds":5,"successThreshold":1,"timeoutSeconds":1},"resources":{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"500m","memory":"512Mi"}},"terminationMessagePath":"/dev/termination-log","terminationMessagePolicy":"File"}],"dnsPolicy":"ClusterFirst","imagePullSecrets":[{"name":"ghcr-secret"}],"nodeSelector":{"kubernetes.io/hostname":"node2"},"restartPolicy":"Always","schedulerName":"default-scheduler","securityContext":{},"terminationGracePeriodSeconds":30}}}}
    creationTimestamp: "2026-04-09T17:30:28Z"
    generation: 2
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-sem-csmf-v2
    namespace: trisla
    resourceVersion: "886497623"
    uid: 0a2abca7-f475-4748-9c8c-b0395b53cc30
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-sem-csmf-v2
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-05T22:48:50-03:00"
        creationTimestamp: null
        labels:
          app: trisla-sem-csmf-v2
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: KAFKA_ENABLED
            value: "true"
          - name: KAFKA_BROKERS
            value: kafka:9092
          - name: DECISION_ENGINE_URL
            value: http://trisla-decision-engine-v2:8082/evaluate
          image: ghcr.io/abelisboa/trisla-sem-csmf@sha256:31f32c78db0c07165c5ac6fa0f2b46af75fcfc5162a214d23ef0bd18f577f541
          imagePullPolicy: IfNotPresent
          livenessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/health",
                timeout=5).read()
            failureThreshold: 5
            initialDelaySeconds: 60
            periodSeconds: 15
            successThreshold: 1
            timeoutSeconds: 6
          name: sem-csmf
          ports:
          - containerPort: 8080
            name: http
            protocol: TCP
          readinessProbe:
            exec:
              command:
              - python3
              - -c
              - import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/health",
                timeout=5).read()
            failureThreshold: 5
            initialDelaySeconds: 30
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 6
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        imagePullSecrets:
        - name: ghcr-secret
        nodeSelector:
          kubernetes.io/hostname: node2
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-09T17:30:28Z"
      lastUpdateTime: "2026-04-09T17:37:28Z"
      message: ReplicaSet "trisla-sem-csmf-v2-5d66d7756d" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:03:24Z"
      lastUpdateTime: "2026-04-12T21:03:24Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 2
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "27"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-02-14T21:18:35Z"
    generation: 33
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-sla-agent-layer
    namespace: trisla
    resourceVersion: "886497676"
    uid: 434e5544-d17c-4a47-b225-774d4528258d
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-sla-agent-layer
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        annotations:
          kubectl.kubernetes.io/restartedAt: "2026-04-05T22:48:50-03:00"
        creationTimestamp: null
        labels:
          app: trisla-sla-agent-layer
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          - name: NASP_ADAPTER_URL
            value: http://trisla-nasp-adapter:8085
          - name: BC_NSSMF_URL
            value: http://trisla-bc-nssmf:8083
          - name: KAFKA_ENABLED
            value: "true"
          - name: KAFKA_BROKERS
            value: kafka.trisla.svc.cluster.local:9092
          image: ghcr.io/abelisboa/trisla-sla-agent-layer@sha256:397fef296ced041745eb9170524a875ac83e1c96e09f0c7248c49d051983f9f3
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 30
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          name: sla-agent-layer
          ports:
          - containerPort: 8084
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 1
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        nodeSelector:
          kubernetes.io/hostname: node2
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-04-01T01:11:09Z"
      lastUpdateTime: "2026-04-06T01:47:15Z"
      message: ReplicaSet "trisla-sla-agent-layer-58d6bd5fc7" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:03:29Z"
      lastUpdateTime: "2026-04-12T21:03:29Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 33
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "1"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"trisla-tempo","namespace":"trisla"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"trisla-tempo"}},"template":{"metadata":{"labels":{"app":"trisla-tempo"}},"spec":{"containers":[{"args":["-config.file=/etc/tempo.yaml"],"image":"grafana/tempo:2.4.1","name":"tempo","ports":[{"containerPort":3200},{"containerPort":4317}],"volumeMounts":[{"mountPath":"/etc/tempo.yaml","name":"config","subPath":"tempo.yaml"}]}],"volumes":[{"configMap":{"name":"trisla-tempo-config"},"name":"config"}]}}}}
    creationTimestamp: "2026-02-25T01:18:00Z"
    generation: 1
    name: trisla-tempo
    namespace: trisla
    resourceVersion: "886041428"
    uid: 6eac2eaa-6204-4db9-9f64-38413809ac68
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-tempo
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        creationTimestamp: null
        labels:
          app: trisla-tempo
      spec:
        containers:
        - args:
          - -config.file=/etc/tempo.yaml
          image: grafana/tempo:2.4.1
          imagePullPolicy: IfNotPresent
          name: tempo
          ports:
          - containerPort: 3200
            protocol: TCP
          - containerPort: 4317
            protocol: TCP
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          volumeMounts:
          - mountPath: /etc/tempo.yaml
            name: config
            subPath: tempo.yaml
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
        volumes:
        - configMap:
            defaultMode: 420
            name: trisla-tempo-config
          name: config
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-02-25T01:18:00Z"
      lastUpdateTime: "2026-02-25T01:18:09Z"
      message: ReplicaSet "trisla-tempo-bcf9bb868" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-11T02:42:03Z"
      lastUpdateTime: "2026-04-11T02:42:03Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 1
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "21"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-02-14T21:18:35Z"
    generation: 25
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: traffic-exporter
      helm.sh/chart: trisla-3.10.0
    name: trisla-traffic-exporter
    namespace: trisla
    resourceVersion: "886496953"
    uid: 00b55427-22ff-4a00-911f-4ecd2f60aba5
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-traffic-exporter
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: traffic-exporter
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        creationTimestamp: null
        labels:
          app: trisla-traffic-exporter
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: traffic-exporter
      spec:
        containers:
        - image: ghcr.io/abelisboa/trisla-traffic-exporter@sha256:a39455f913ea4f7355426b48613cc0479c7e549d099bdba520fd4fb563564f48
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: metrics
              scheme: HTTP
            initialDelaySeconds: 15
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          name: exporter
          ports:
          - containerPort: 9105
            name: metrics
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: metrics
              scheme: HTTP
            initialDelaySeconds: 5
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 1
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        serviceAccount: trisla-traffic-exporter
        serviceAccountName: trisla-traffic-exporter
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-10T17:37:46Z"
      lastUpdateTime: "2026-03-11T17:21:10Z"
      message: ReplicaSet "trisla-traffic-exporter-79ff48f977" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-12T21:02:19Z"
      lastUpdateTime: "2026-04-12T21:02:19Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 25
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "4"
      meta.helm.sh/release-name: trisla
      meta.helm.sh/release-namespace: trisla
    creationTimestamp: "2026-03-30T03:10:20Z"
    generation: 4
    labels:
      app.kubernetes.io/instance: trisla
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: trisla
      helm.sh/chart: trisla-3.10.0
    name: trisla-ui-dashboard
    namespace: trisla
    resourceVersion: "885177733"
    uid: 71a9ef36-739e-46b3-a933-43d3ce00786c
  spec:
    progressDeadlineSeconds: 600
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: trisla-ui-dashboard
        app.kubernetes.io/instance: trisla
        app.kubernetes.io/name: trisla
    strategy:
      rollingUpdate:
        maxSurge: 25%
        maxUnavailable: 25%
      type: RollingUpdate
    template:
      metadata:
        creationTimestamp: null
        labels:
          app: trisla-ui-dashboard
          app.kubernetes.io/instance: trisla
          app.kubernetes.io/name: trisla
      spec:
        containers:
        - env:
          - name: TRISLA_NODE_INTERFACE
            value: my5g
          - name: TRISLA_NODE_IP
            value: 192.168.10.16
          - name: OTLP_ENDPOINT
            value: http://trisla-otel-collector:4317
          image: ghcr.io/abelisboa/trisla-ui-dashboard@sha256:16e23f4de91582e56bfe4704c0139a3154c34c4a44780f17f3082b6195dbe6fb
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 120
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          name: ui-dashboard
          ports:
          - containerPort: 80
            name: http
            protocol: TCP
          readinessProbe:
            failureThreshold: 6
            httpGet:
              path: /health
              port: http
              scheme: HTTP
            initialDelaySeconds: 60
            periodSeconds: 5
            successThreshold: 1
            timeoutSeconds: 5
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        nodeSelector:
          kubernetes.io/hostname: node1
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
  status:
    availableReplicas: 1
    conditions:
    - lastTransitionTime: "2026-03-30T03:10:20Z"
      lastUpdateTime: "2026-04-07T09:17:14Z"
      message: ReplicaSet "trisla-ui-dashboard-c9545c94" has successfully progressed.
      reason: NewReplicaSetAvailable
      status: "True"
      type: Progressing
    - lastTransitionTime: "2026-04-07T14:48:07Z"
      lastUpdateTime: "2026-04-07T14:48:07Z"
      message: Deployment has minimum availability.
      reason: MinimumReplicasAvailable
      status: "True"
      type: Available
    observedGeneration: 4
    readyReplicas: 1
    replicas: 1
    updatedReplicas: 1
kind: List
metadata:
  resourceVersion: ""

## ENDPOINTS REAIS
Portal Backend:
NAME                               TYPE           CLUSTER-IP      EXTERNAL-IP                                                          PORT(S)                       AGE
prometheus                         ExternalName   <none>          monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local   <none>                        81d
svc-trisla-trisla                  ClusterIP      10.233.8.139    <none>                                                               8001/TCP                      3d19h
svc-trisla-v1                      ClusterIP      10.233.15.210   <none>                                                               8001/TCP                      3d19h
svc-trisla-v2                      ClusterIP      10.233.59.234   <none>                                                               8001/TCP                      3d19h
trisla-analytics-adapter           ClusterIP      10.233.6.69     <none>                                                               8080/TCP                      72d
trisla-analytics-adapter-metrics   ClusterIP      10.233.16.227   <none>                                                               8080/TCP                      40d
trisla-bc-nssmf                    ClusterIP      10.233.39.215   <none>                                                               8083/TCP                      114d
trisla-bc-nssmf-metrics            ClusterIP      10.233.30.108   <none>                                                               8083/TCP                      113d
trisla-besu                        ClusterIP      10.233.54.19    <none>                                                               8545/TCP,8546/TCP,30303/TCP   71d
trisla-blockchain-exporter         ClusterIP      10.233.11.248   <none>                                                               8000/TCP                      39d
trisla-decision-engine             ClusterIP      10.233.26.201   <none>                                                               8082/TCP                      114d
trisla-decision-engine-metrics     ClusterIP      10.233.32.162   <none>                                                               8082/TCP                      113d
trisla-decision-engine-trisla      ClusterIP      10.233.15.143   <none>                                                               8082/TCP                      3d19h
trisla-decision-engine-v1          ClusterIP      10.233.32.245   <none>                                                               8082/TCP                      3d19h
trisla-decision-engine-v2          ClusterIP      10.233.26.245   <none>                                                               8082/TCP                      3d19h
trisla-iperf3                      ClusterIP      10.233.18.180   <none>                                                               5201/TCP                      81d
trisla-ml-nsmf                     ClusterIP      10.233.28.209   <none>                                                               8081/TCP                      114d
trisla-ml-nsmf-metrics             ClusterIP      10.233.23.11    <none>                                                               8081/TCP                      40d
trisla-nasp-adapter                ClusterIP      10.233.6.35     <none>                                                               8085/TCP                      114d
trisla-nasp-adapter-metrics        ClusterIP      10.233.12.198   <none>                                                               8085/TCP                      40d
trisla-network-exporter            ClusterIP      10.233.52.111   <none>                                                               8000/TCP                      39d
trisla-otel-collector              ClusterIP      10.233.44.57    <none>                                                               4317/TCP,4318/TCP             47d
trisla-portal-backend              NodePort       10.233.46.159   <none>                                                               8001:32002/TCP                113d
trisla-portal-backend-metrics      ClusterIP      10.233.54.110   <none>                                                               8001/TCP                      40d
trisla-portal-frontend             NodePort       10.233.18.2     <none>                                                               80:32561/TCP                  26d
trisla-prb-simulator               ClusterIP      10.233.54.221   <none>                                                               8086/TCP                      20d
trisla-ran-ue-upf-proxy            ClusterIP      10.233.24.53    <none>                                                               9102/TCP                      2d11h
trisla-sem-csmf                    ClusterIP      10.233.13.160   <none>                                                               8080/TCP                      114d
trisla-sem-csmf-metrics            ClusterIP      10.233.59.110   <none>                                                               8080/TCP                      40d
trisla-sem-csmf-trisla             ClusterIP      10.233.6.137    <none>                                                               8080/TCP                      3d19h
trisla-sem-csmf-v1                 ClusterIP      10.233.15.172   <none>                                                               8080/TCP                      3d19h
trisla-sem-csmf-v2                 ClusterIP      10.233.11.15    <none>                                                               8080/TCP                      3d19h
trisla-sla-agent-layer             ClusterIP      10.233.4.83     <none>                                                               8084/TCP                      114d
trisla-sla-agent-metrics           ClusterIP      10.233.25.234   <none>                                                               8084/TCP                      113d
trisla-tempo                       ClusterIP      10.233.35.78    <none>                                                               3200/TCP,4317/TCP             47d
trisla-traffic-exporter            ClusterIP      10.233.37.239   <none>                                                               9105/TCP                      71d
trisla-ui-dashboard                ClusterIP      10.233.28.172   <none>                                                               80/TCP                        14d

## PIPELINE REAL TRI-SLA

User Request
? Portal Backend
? SEM-NSMF
? ML-NSMF
? Decision Engine
? NASP Orchestration

RAN:
- UERANSIM
- uesimtun0 (10.1.0.x)

Transport:
- ONOS
- Mininet

Core:
- AMF / SMF / UPF

Data Plane:
UE ? GTP-U ? UPF ? N6 (Multus net1) ? Peer ? retorno

## Core CPU and Memory Metrics (Aligned Implementation)

Core resource utilization is measured using container-level metrics scoped to the Core namespace.

These metrics are configured via runtime environment variables:

- TELEMETRY_PROMQL_CORE_CPU
- TELEMETRY_PROMQL_CORE_MEMORY

Example:

CPU:
sum(rate(container_cpu_usage_seconds_total{namespace="<core_ns>", container!="", container!="POD"}[2m])) / sum(machine_cpu_cores)

Memory:
sum(container_memory_working_set_bytes{namespace="<core_ns>", container!="", container!="POD"}) / sum(machine_memory_bytes)

Note:
Previous process-level metrics (`process_*`) were deprecated due to lack of domain specificity.

### Transport Jitter (Final Role Definition)

Transport-level jitter is collected via probe-based telemetry and used for observability.

It does not directly influence the decision engine.

Jitter is only considered as part of SLA-defined requirements and contributes indirectly through ML-based risk estimation.

### Decision Hierarchy

1. RAN (PRB) -> Hard constraint
2. Transport -> QoS refinement
3. Core -> Context only
