import sys
import os
import yaml


def output_env_vars(file_path):
    """
    Extracts local env vars and secrets from a YAML file and prints then as export statements
    Args:
    - file_path (str): Path to the YAML file containing environment variables and secrets.

    """
    if not os.path.isfile(file_path):
        print(f"File '{file_path}' not found.")
        return

    with open(file_path, "r") as yaml_file:
        try:
            yaml_data = yaml.safe_load(yaml_file)
        except yaml.YAMLError as e:
            print(f"Error loading YAML file '{file_path}': {e}")
            return

    # Output variables
    if "env_vars" in yaml_data:
        env_vars = yaml_data["env_vars"]
        for item in env_vars:
            for key, value in item.items():
                print(f'export {key}="{value}"')

    # Output secrets
    if "secrets" in yaml_data:
        secrets = yaml_data["secrets"]
        for _category, secret_data in secrets.items():
            if "secret_values" in secret_data:
                for item in secret_data["secret_values"]:
                    for key, value in item.items():
                        print(f'export {key}="{value}"')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load_local_env_vars.py <yaml-file>")
        sys.exit(1)

    file_path = sys.argv[1]
    output_env_vars(file_path)
