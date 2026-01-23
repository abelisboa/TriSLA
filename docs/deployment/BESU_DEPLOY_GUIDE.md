# BESU Module Deployment Guide - TriSLA

**Version:** 3.7.10  
**Date:** 2025-01-15  
**Module:** Hyperledger Besu - Blockchain Client

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Deployment (Docker)](#local-deployment-docker)
4. [Kubernetes Deployment (NASP)](#kubernetes-deployment-nasp)
5. [Validation](#validation)
6. [Troubleshooting](#troubleshooting)
7. [Rollback](#rollback)

---

## 🎯 Overview

The BESU module provides the permissioned blockchain infrastructure required for BC-NSSMF to register SLAs on-chain. It implements a permissioned Ethereum blockchain using Hyperledger Besu.

### Features

- **Permissioned Blockchain**: Hyperledger Besu
- **Chain ID**: 1337
- **Consensus**: IBFT2 (dev mode)
- **RPC Endpoint**: HTTP on port 8545
- **Persistence**: Persistent volume for blockchain data

---

## ✅ Prerequisites

### Local (Docker)

- Docker Desktop or Docker Engine
- Docker Compose (optional)
-  for testing

### Kubernetes (NASP)

- Accessible Kubernetes cluster
- kubectl controls the Kubernetes cluster manager.

 Find more information at: https://kubernetes.io/docs/reference/kubectl/

Basic Commands (Beginner):
  create          Create a resource from a file or from stdin
  expose          Take a replication controller, service, deployment or pod and expose it as a new Kubernetes service
  run             Executa uma imagem específica no cluster
  set             Define funcionalidades específicas em objetos

Basic Commands (Intermediate):
  explain         Get documentation for a resource
  get             Mostra um ou mais recursos
  edit            Edita um recurso no servidor
  delete          Delete resources by file names, stdin, resources and names, or by resources and label selector

Deploy Commands:
  rollout         Manage the rollout of a resource
  scale           Set a new size for a deployment, replica set, or replication controller
  autoscale       Auto-scale a deployment, replica set, stateful set, or replication controller

Cluster Management Commands:
  certificate     Modify certificate resources
  cluster-info    Display cluster information
  top             Display resource (CPU/memory) usage
  cordon          Marca o node como não agendável
  uncordon        Marca o node como agendável
  drain           Drenar o node para preparação de manutenção
  taint           Atualizar o taints de um ou mais nodes

Troubleshooting and Debugging Commands:
  describe        Mostra os detalhes de um recurso específico ou de um grupo de recursos
  logs            Mostra os logs de um container em um pod
  attach          Se conecta a um container em execução
  exec            Executa um comando em um container
  port-forward    Encaminhar uma ou mais portas locais para um pod
  proxy           Executa um proxy para o servidor de API do Kubernetes
  cp              Copy files and directories to and from containers
  auth            Inspect authorization
  debug           Create debugging sessions for troubleshooting workloads and nodes
  events          List events

Advanced Commands:
  diff            Diff the live version against a would-be applied version
  apply           Apply a configuration to a resource by file name or stdin
  patch           Update fields of a resource
  replace         Replace a resource by file name or stdin
  wait            Experimental: Wait for a specific condition on one or many resources
  kustomize       Build a kustomization target from a directory or URL

Settings Commands:
  label           Atualizar os labels de um recurso
  annotate        Atualizar as anotações de um recurso
  completion      Output shell completion code for the specified shell (bash, zsh, fish, or powershell)

Other Commands:
  api-resources   Print the supported API resources on the server
  api-versions    Print the supported API versions on the server, in the form of "group/version"
  config          Edita o arquivo kubeconfig
  plugin          Provides utilities for interacting with plugins
  version         Mostra a informação de versão do cliente e do servidor

Usage:
  kubectl [flags] [options]

Use "kubectl <command> --help" for more information about a given command.
Use "kubectl options" for a list of global command-line options (applies to all commands). configured
- The Kubernetes package manager

Common actions for Helm:

- helm search:    search for charts
- helm pull:      download a chart to your local directory to view
- helm install:   upload the chart to Kubernetes
- helm list:      list releases of charts

Environment variables:

| Name                               | Description                                                                                       |
|------------------------------------|---------------------------------------------------------------------------------------------------|
| $HELM_CACHE_HOME                   | set an alternative location for storing cached files.                                             |
| $HELM_CONFIG_HOME                  | set an alternative location for storing Helm configuration.                                       |
| $HELM_DATA_HOME                    | set an alternative location for storing Helm data.                                                |
| $HELM_DEBUG                        | indicate whether or not Helm is running in Debug mode                                             |
| $HELM_DRIVER                       | set the backend storage driver. Values are: configmap, secret, memory, sql.                       |
| $HELM_DRIVER_SQL_CONNECTION_STRING | set the connection string the SQL storage driver should use.                                      |
| $HELM_MAX_HISTORY                  | set the maximum number of helm release history.                                                   |
| $HELM_NAMESPACE                    | set the namespace used for the helm operations.                                                   |
| $HELM_NO_PLUGINS                   | disable plugins. Set HELM_NO_PLUGINS=1 to disable plugins.                                        |
| $HELM_PLUGINS                      | set the path to the plugins directory                                                             |
| $HELM_REGISTRY_CONFIG              | set the path to the registry config file.                                                         |
| $HELM_REPOSITORY_CACHE             | set the path to the repository cache directory                                                    |
| $HELM_REPOSITORY_CONFIG            | set the path to the repositories file.                                                            |
| $KUBECONFIG                        | set an alternative Kubernetes configuration file (default "~/.kube/config")                       |
| $HELM_KUBEAPISERVER                | set the Kubernetes API Server Endpoint for authentication                                         |
| $HELM_KUBECAFILE                   | set the Kubernetes certificate authority file.                                                    |
| $HELM_KUBEASGROUPS                 | set the Groups to use for impersonation using a comma-separated list.                             |
| $HELM_KUBEASUSER                   | set the Username to impersonate for the operation.                                                |
| $HELM_KUBECONTEXT                  | set the name of the kubeconfig context.                                                           |
| $HELM_KUBETOKEN                    | set the Bearer KubeToken used for authentication.                                                 |
| $HELM_KUBEINSECURE_SKIP_TLS_VERIFY | indicate if the Kubernetes API server's certificate validation should be skipped (insecure)       |
| $HELM_KUBETLS_SERVER_NAME          | set the server name used to validate the Kubernetes API server certificate                        |
| $HELM_BURST_LIMIT                  | set the default burst limit in the case the server contains many CRDs (default 100, -1 to disable)|

Helm stores cache, configuration, and data based on the following configuration order:

- If a HELM_*_HOME environment variable is set, it will be used
- Otherwise, on systems supporting the XDG base directory specification, the XDG variables will be used
- When no other location is set a default location will be used based on the operating system

By default, the default directories depend on the Operating System. The defaults are listed below:

| Operating System | Cache Path                | Configuration Path             | Data Path               |
|------------------|---------------------------|--------------------------------|-------------------------|
| Linux            | $HOME/.cache/helm         | $HOME/.config/helm             | $HOME/.local/share/helm |
| macOS            | $HOME/Library/Caches/helm | $HOME/Library/Preferences/helm | $HOME/Library/helm      |
| Windows          | %TEMP%\helm               | %APPDATA%\helm                 | %APPDATA%\helm          |

Usage:
  helm [command]

Available Commands:
  completion  generate autocompletion scripts for the specified shell
  create      create a new chart with the given name
  dependency  manage a chart's dependencies
  env         helm client environment information
  get         download extended information of a named release
  help        Help about any command
  history     fetch release history
  install     install a chart
  lint        examine a chart for possible issues
  list        list releases
  package     package a chart directory into a chart archive
  plugin      install, list, or uninstall Helm plugins
  pull        download a chart from a repository and (optionally) unpack it in local directory
  push        push a chart to remote
  registry    login to or logout from a registry
  repo        add, list, remove, update, and index chart repositories
  rollback    roll back a release to a previous revision
  search      search for a keyword in charts
  show        show information of a chart
  status      display the status of the named release
  template    locally render templates
  test        run tests for a release
  uninstall   uninstall a release
  upgrade     upgrade a release
  verify      verify that a chart at the given path has been signed and is valid
  version     print the client version information

Flags:
      --burst-limit int                 client-side default throttling limit (default 100)
      --debug                           enable verbose output
  -h, --help                            help for helm
      --kube-apiserver string           the address and the port for the Kubernetes API server
      --kube-as-group stringArray       group to impersonate for the operation, this flag can be repeated to specify multiple groups.
      --kube-as-user string             username to impersonate for the operation
      --kube-ca-file string             the certificate authority file for the Kubernetes API server connection
      --kube-context string             name of the kubeconfig context to use
      --kube-insecure-skip-tls-verify   if true, the Kubernetes API server's certificate will not be checked for validity. This will make your HTTPS connections insecure
      --kube-tls-server-name string     server name to use for Kubernetes API server certificate validation. If it is not provided, the hostname used to contact the server is used
      --kube-token string               bearer token used for authentication
      --kubeconfig string               path to the kubeconfig file
  -n, --namespace string                namespace scope for this request
      --registry-config string          path to the registry config file (default "/home/porvir5g/.config/helm/registry/config.json")
      --repository-cache string         path to the file containing cached repository indexes (default "/home/porvir5g/.cache/helm/repository")
      --repository-config string        path to the file containing repository names and URLs (default "/home/porvir5g/.config/helm/repositories.yaml")

Use "helm [command] --help" for more information about a command. v3.x installed
- Access to  namespace
- StorageClass configured (for persistence)

---

## 🐳 Local Deployment (Docker)

### 1. Start BESU



The script will:
- Check Docker
- Stop existing container (if any)
- Start BESU via docker-compose
- Wait for initialization (30s)
- Validate HTTP RPC

### 2. Check Status



Expected output:


### 3. Validate Integration with BC-NSSMF



### 4. Stop BESU



---

## ☸️ Kubernetes Deployment (NASP)

### 1. Prepare Values

The file  already contains BESU configuration:



### 2. Update Images (if necessary)



### 3. Access NASP Cluster



### 4. Apply Helm Chart Upgrade

==> Linting helm/trisla
[INFO] Chart.yaml: icon is recommended
[INFO] values.yaml: file does not exist
[ERROR] templates/: parse error at (trisla/templates/prometheusrules/category-d-capacity-saturation.yaml:33): undefined variable "$labels"

### 5. Verify Deployment



### 6. Test RPC



Expected response:


---

## ✅ Validation

### 1. Verify BESU



### 2. Verify BC-NSSMF



### 3. Test SLA Registration



Expected response:


---

## 🛠️ Troubleshooting

### Issue: BESU does not start

**Symptoms:**
- Container stops immediately
- Logs show genesis.json error

**Solution:**


### Issue: BC-NSSMF cannot connect to BESU

**Symptoms:**
- BC-NSSMF returns 
- Error: BC-NSSMF is in degraded mode

**Solution:**
1. Verify BESU is running:
   

2. Check BC-NSSMF environment variables:
   

3. Test connectivity:
   

4. Check service:
   

### Issue: PVC is not created

**Symptoms:**
- Pod stays in 
- Event: no persistent volumes available

**Solution:**
1. Check StorageClass:
   

2. Adjust :
   

3. Or disable persistence (not recommended for production):
   

---

## 🔄 Rollback

### Helm Rollback



### Manual Rollback



---

## 📊 Monitoring

### Metrics

BESU exposes metrics via RPC:



### Structured Logs

BESU logs include:
- Blockchain initialization
- Block creation
- RPC connections
- Errors and warnings

---

## 📚 References

- [Hyperledger Besu Documentation](https://besu.hyperledger.org/)
- [TriSLA BC-NSSMF Guide](../bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md)
- [Helm Chart Documentation](../../helm/trisla/README.md)

---

*Last updated: 2025-01-15*
