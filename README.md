## Local Development Guide

### Tools Used
- Python 3.11
- Poetry
- Alembic
- Kubernetes

### Development Tools Used
- mypy
- black
- flake8 (with flake8-length)
- git pre-commit hooks

### Setting Up Local Environment for Python Development

1. **Install Python 3.11:**
   - Make sure Python 3.11 is installed on your system. You can download it from [Python.org](https://www.python.org/downloads/).

2. **Install Poetry:**
   - Install Poetry using the following command:
     ```bash
     curl -sSL https://install.python-poetry.org | python3 -
     ```
   - Verify Poetry installation:
     ```bash
     poetry --version
     ```

3. **Set Default Python Version for Poetry:**
   - Make sure Poetry uses Python 3.11 as the default:
     ```bash
     poetry env use python3.11
     poetry run python --version
     ```

### Vscode Development
If you are using vscode, the `.vscode` directory contains the following:
- `extensions.json`: contains the recommended vscode extensions for this project
- `settings.json`: contains the default configs for this project

### Environment variables and Secrets
   - The app has a number of env variables such as database hostname and creds that it is looking for. To quickly reference which ones you need to set, check out the
   file `.env-vars-test.yaml`. If you update the env vars or secrets being looked for, you will also need to update this file.  Secrets and env variables are treated similarly by the app and database pods, but since they contain sensitive data, we use k8s secrets to encrypt and store them.


   1. **K8s Environment Variables**
   
   - To populate these variables into your k8s containers, copy the file to a file which is named: 
   ```bash
   .env-vars-k8s.yaml
   ```
    and then update with the correct credentials. DO NOT COMMIT THIS FILE TO GIT. It is in gitignore, so you shouldn't be able to do that accidentally. 

   2. **Local Development Environment Variables**
   - For local development, create a file in the same format as `.env-vars-k8s.yaml` and call it:
   ```bash
   .env-vars-local.yaml
   ```
   Also do not commmit this file to git. 

   To populate these variables into your shell environment, run:
   ```bash
   . local_dev_scripts/load_local_env_vars.sh .env-vars-local.yaml
   ```
   NOTE: that's a dot and a space before the script name. you need to use that to get it to exeucte in the same shell as you're currently in. You will need to do this every time you log into a new shell. 

### Setting Up Your K8s Database Pod (First run)
If you are running end to end testing using your kubernetes app pod, you will probably want to go ahead and stand this db pod up as well since the k8s pod will automatically be able to connect to it.

1.  **Deploy The Pod**
After making sure you have the correct values in your `.env-vars-k8s.yaml` or whatever you named your local dev yaml file containing these values, you run: 
   ```bash
   make db
   ```
2. **Initialize the Database**
   - If this is your first time running the pod, it will not come with the expected users or schema. You can run a local python script that will use the env variables you populated in #1 to connect to the database and create the schema if it exists, then add the required users and grant them the correct permissions.

   - First, make sure that you have followed the instructions above under "Local Development Environment Variables" to populate the env variables into your shells ession. 

   - Next, you can run the following file which will connect to the database and initialize the user and databases needed for the app: 
   ```bash
   poetry run python local_dev_scripts/init_local_db.py
   ```

4. **(Optional) Open the Port to Local Connections***
   - By default only other k8s pods can connect to the database. To enable port forwarding, so you can connect with a SQL client, or from a locally run script, you can run:

    ```bash
    kubectl port-forward service/db 3306:3306 & #& to run in the background
    ```
   - to stop port forwarding run:
    ```bash
    ps aux | grep port-forward
    ```
    then use the `kill` command to kill the pid you find.

### Kubernetes App Development
1.  **Deploy The Pods**
   - After making sure you have the correct values in your `.env-vars-k8s.yaml` or whatever you named your local dev yaml file containing these values, you can run: 
   ```bash
   make
   ```
   This will both load and update your env variables, and start both your database and app containers if they are not started, and apply the newest 
   - Whenever you make changes to your application code or dependencies, you will need to apply your changes to the k8s pod using the same make command. 

2. **Apply Changes to Dockerfile (Make Clean)**
   - If you make major changes to the app Dockerfile such as altering the base image or changing the commands significantly, or you are likely to need to rebuild the docker image without cache. 
   You can do this using:
     ```bash
     make clean
     ```
   This will apply any db changes normally, and then build the app docker image without cache and apply your changes to the kubernetes pods. 

3. **Apply Structural Changes (Make Supeclean)**
   -  For certain changes, you may need to really blow things up, meaning delete the deployments and pods and start over. These changes would be things like:
      * Image pull policy changes (`IfNotPresent` > `Always` or similar)
      * Volume changes (changes to `.db-pvc.yaml`)
      * Port changes
      * Security context changes
      * Really heavy duty ConfigMap/Secret Changes. Most shouldn't need this, but big changes might. 
   
   You can do this using:
   ```bash
   make superclean
   ```

   This will delete the deployments and pods for both the app and db, then rebuild the app docker image without cache, and then reapply all files for both the app and db. 


### Basic Kubernetes Commands
   - Here are some useful Kubernetes commands to interact with your deployment:
     ```bash
     kubectl get pods              # List all pods
     kubectl describe pod <pod name>    # Describe a specific pod
     kubectl logs <pod name>       # View logs of a specific pod
     ```

For more detailed Kubernetes documentation, visit [Kubernetes Documentation](https://kubernetes.io/docs/).


### Local Development in Python (Without Kubernetes)
To avoid having to build the docker container every time you make code changes, you can run your python code locally using poetry. If you do this, you can still use the MySQL k8s pod, but you could also just install a local version of MySQL probably.

1. **Populate Your Env Variables**
   - After making sure you have the correct values in your `.env-vars-local.yaml` or whatever you named your local dev yaml file containing these values, you can use the script `local_dev_scripts/load_local_env_vars.sh` to export those values into your local terminal environment variables.

   This script actually just calling a python script that grabs the values from the yaml and evaluating the output in the local bash shell. But if it is possible to get python to set environment variables in your local shell, it is probably bad to do so security-wise. It is possible and fine to evaluate yaml using bash, but you'd have to install jq locally and that's not a default offering on a lot of machines.

   When you run this script, you have to use *dot-space syntax* which executes in your local shell. So instead of `./path/to/my_script.sh`, you need to run `. path/to/my_script.sh`.

   ```bash
   . local_dev_scripts/load_local_env_vars.sh .env-vars-local.yaml
   ```
2. **Make Changes and Run Locally**
   - Use `poetry run python <script path>` to run your script.
