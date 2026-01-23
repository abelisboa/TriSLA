# TriSLA Portal Backend

Backend service for the TriSLA Observability Portal, built with FastAPI (Python 3.11).

## Installation

The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.13-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.

Failing command: /home/porvir5g/gtp5g/venv/bin/python

## Development



Access [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger API documentation.

## Project Structure



## API Endpoints

-  - Health check
-  - TriSLA modules status
-  - Prometheus metrics queries
-  - Loki logs queries
-  - Tempo traces queries
-  - SLA intent processing
-  - SLA contract management
-  - SLA operations
-  - Explainable AI endpoints
-  - SLO management

## Docker



## Kubernetes

Deploy using Helm charts in .

## Environment Variables

See  for required environment variables.

## Version

Part of TriSLA v3.9.3 (frozen scientific version).
