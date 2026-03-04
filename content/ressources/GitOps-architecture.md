---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== You can decompress Drawing data with the command palette: 'Decompress current Excalidraw file'. For more info check in plugin settings under 'Saving'


# Excalidraw Data

## Text Elements
|-- apps
|   |-- base
|   |   `-- linkding
|   |       |-- kustomization.yaml
|   |       `-- deployment.yaml
|   `-- staging
|       `-- linkding
|           |-- kustomization.yaml
|           `-- ingress.yaml
|
|-- clusters
|   `-- staging
|       |-- apps.yaml
|       |-- flux-system
|       |   |-- gotk-components.yaml
|       |   |-- gotk-sync.yaml
|       |   `-- kustomization.yaml
|       `-- monitoring.yaml
|
|-- monitoring
|   |-- configs
|   |   |-- base
|   |   `-- staging
|   `-- controllers
|       |-- base
|       |   `-- kube-prometheus-stack
|       |       |-- kustomization.yaml
|       |       |-- namespace.yaml
|       |       |-- release.yaml
|       |       `-- repository.yaml
|       `-- staging
|           |-- kube-prometheus-stack
|           |   `-- kustomization.yaml
|           `-- kustomization.yaml ^wfeAc1G5

|-- User application (main services)
|   |-- Configuration that doesn't change in any case
|   |   `-- Service name
|   |       |-- File where you declare the files needed to deploy on the cluster
|   |       `-- Ressources definition
|   `-- Specific cluster type (dev, staging, production, ...)
|       `-- Service name
|           |-- File where you declare the files needed to deploy on the cluster
|           `-- Ressources definition
|
|-- Contain your clusters with Flux configuration
|   `-- Specific cluster type (dev, staging, production, ...)
|       |-- Redirect Flux to synchronize the apps directory.
|       |-- Internal Flux configuration (do not touch is you don't know)
|       |   |-- Internal Flux config
|       |   |-- Internal Flux config
|       |   `-- kustomization.yaml
|       `-- Redirect Flux to synchronize the monitoring directory.
|
|-- All your monitoring stack (Prometheus, Grafana, ...)
|   |-- configs
|   |   |-- base
|   |   `-- staging
|   `-- controllers
|       |-- base
|       |   `-- kube-prometheus-stack
|       |       |-- kustomization.yaml
|       |       |-- namespace.yaml
|       |       |-- release.yaml
|       |       `-- repository.yaml
|       `-- staging
|           |-- kube-prometheus-stack
|           |   `-- kustomization.yaml
|           `-- kustomization.yaml ^9e9QqQiz

%%
## Drawing
```compressed-json
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

ystLwKqcghBjxg1wBFk6B7dor5kQB5kgA===
```
%%