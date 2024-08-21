import os
import yaml


def load_env_vars_from_yaml(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)

    # Set environment variables
    for env_var in config.get("env_vars", []):
        for key, value in env_var.items():
            os.environ[key] = str(value)

    # Load secrets (if needed for testing)
    for secret_group in config.get("secrets", {}).values():
        for secret in secret_group.get("secret_values", []):
            for key, value in secret.items():
                os.environ[key] = str(value)
