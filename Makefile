# Variables
KUBE_NAMESPACE = default
KUBE_LABEL_APP = app
KUBE_LABEL_DB = db

# Commands
PYTHON = poetry run python
POETRY = poetry
DOCKER = docker
KUBECTL = kubectl


# Targets
.PHONY: setup clean clean-app clean-db local-env-vars port-forward init-local-db

setup: load-k8s-vars apply-k8s

load-k8s-vars:
	$(PYTHON) local_dev_scripts/load_k8s_vars.py .env-vars-k8s.yaml

apply-k8s:
	$(KUBECTL) apply -f db-pvc.yaml
	$(KUBECTL) apply -f db-deployment.yaml
	$(KUBECTL) apply -f db-service.yaml
	$(KUBECTL) apply -f app-service.yaml
	$(KUBECTL) apply -f app-deployment.yaml

db: load-k8s-vars apply-db

apply-db:
	$(KUBECTL) apply -f db-pvc.yaml
	$(KUBECTL) apply -f db-deployment.yaml
	$(KUBECTL) apply -f db-service.yaml

app: load-k8s-vars apply-app

apply-app:
	$(DOCKER) build --no-cache -t app .
	$(KUBECTL) apply -f app-service.yaml
	$(KUBECTL) apply -f app-deployment.yaml

clean: load-k8s-vars apply-db
	$(DOCKER) build --no-cache -t app .
	$(KUBECTL) apply -f app-service.yaml
	$(KUBECTL) apply -f app-deployment.yaml

superclean: suplerclean-app superclean-db

superclean-app: load-k8s-vars
	-$(KUBECTL) delete deployment app || true
	-$(KUBECTL) delete pod -l $(KUBE_LABEL_APP)=$(KUBE_LABEL_APP) -n $(KUBE_NAMESPACE) || true
	$(DOCKER) build --no-cache -t app .
	$(KUBECTL) apply -f app-deployment.yaml

superclean-db: load-k8s-vars
	-$(KUBECTL) delete deployment db || true
	-$(KUBECTL) delete pod -l $(KUBE_LABEL_DB)=$(KUBE_LABEL_DB) -n $(KUBE_NAMESPACE) || true
	$(KUBECTL) apply -f db-deployment.yaml
