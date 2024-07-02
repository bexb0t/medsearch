import sys
import os
import yaml
from kubernetes import config
from kubernetes.client import CoreV1Api as k8s_api_client
from kubernetes.client import V1ConfigMap as k8s_configmap
from kubernetes.client import V1ObjectMeta as k8s_metadata
from kubernetes.client import V1Secret as k8s_secret
from kubernetes.client.exceptions import ApiException


def load_k8s_vars(file_path):
    """
    Loads Kubernetes ConfigMap and Secrets from a YAML file and creates or updates them in the cluster.

    Args:
    - file_path (str): Path to the YAML file containing environment variables and secrets.

    For structure and expected values, reference the .env-vars-test.yaml which is committed to the repo.

    This script is intended for local development use only.
    """

    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    # Load kubeconfig file (optional if running outside Kubernetes cluster)
    config.load_kube_config()

    # Create a Kubernetes client instance
    client = k8s_api_client()

    # Read YAML file
    with open(file_path, "r") as yaml_file:
        try:
            yaml_data = yaml.safe_load(yaml_file)
        except yaml.YAMLError as e:
            print(f"Error loading YAML file: {e}")
            sys.exit(1)

    # Process environment variables
    if "env_vars" in yaml_data:
        env_vars = yaml_data["env_vars"]
        data = {key: str(value) for item in env_vars for key, value in item.items()}
        create_or_update_configmap(client, data, "env")

    # Process app secrets
    if "secrets" in yaml_data and "app" in yaml_data["secrets"]:
        app_secrets = yaml_data["secrets"]["app"]
        if "secret_values" in app_secrets:
            secret_data = {
                key: str(value)
                for item in app_secrets["secret_values"]
                for key, value in item.items()
            }
            create_or_update_secret(client, secret_data, app_secrets["secret_name"])

    # Process db secrets
    if "secrets" in yaml_data and "db" in yaml_data["secrets"]:
        db_secrets = yaml_data["secrets"]["db"]
        if "secret_values" in db_secrets:
            secret_data = {
                key: value
                for item in db_secrets["secret_values"]
                for key, value in item.items()
            }
            create_or_update_secret(client, secret_data, db_secrets["secret_name"])


def resource_exists(client, name, namespace, resource_type):
    """
    Checks if a Kubernetes resource exists.

    Args:
    - client (k8s_api_client): Kubernetes client instance.
    - name (str): Name of the resource.
    - namespace (str): Namespace of the resource.
    - resource_type (str): Type of the resource ("configmap" or "secret").

    Returns:
    - bool: True if the resource exists, False otherwise.
    """
    try:
        if resource_type == "configmap":
            client.read_namespaced_config_map(name=name, namespace=namespace)
        elif resource_type == "secret":
            client.read_namespaced_secret(name=name, namespace=namespace)
        return True
    except ApiException as e:
        if e.status == 404:
            return False
        else:
            raise e


def create_or_update_configmap(client, data, configmap_name):
    """
    Creates or updates a Kubernetes ConfigMap with the provided data.

    Args:
    - client (k8s_api_client): Kubernetes client instance.
    - data (dict): Dictionary containing key-value pairs for the ConfigMap data.
    - configmap_name (str): Name of the ConfigMap.
    """
    body = k8s_configmap(metadata=k8s_metadata(name=configmap_name), data=data)

    if resource_exists(client, configmap_name, "default", "configmap"):
        client.replace_namespaced_config_map(
            name=configmap_name, namespace="default", body=body
        )
        print(f"Kubernetes ConfigMap '{configmap_name}' updated.")
    else:
        client.create_namespaced_config_map(namespace="default", body=body)
        print(f"Kubernetes ConfigMap '{configmap_name}' created.")


def create_or_update_secret(client, data, secret_name):
    """
    Creates or updates a Kubernetes Secret with the provided data.

    Args:
    - client (k8s_api_client): Kubernetes client instance.
    - data (dict): Dictionary containing key-value pairs for the Secret data.
    - secret_name (str): Name of the Secret.
    """

    body = k8s_secret(metadata=k8s_metadata(name=secret_name), string_data=data)

    if resource_exists(client, secret_name, "default", "secret"):
        client.replace_namespaced_secret(
            name=secret_name, namespace="default", body=body
        )
        print(f"Kubernetes secret '{secret_name}' updated.")
    else:
        client.create_namespaced_secret(namespace="default", body=body)
        print(f"Kubernetes secret '{secret_name}' created.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load_k8s_vars.py <yaml-file>")
        sys.exit(1)

    load_k8s_vars(sys.argv[1])
