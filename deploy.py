#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime

SERVER_ADDRESS = "nucubuntunl"
SERVER_PORT = "5001"
JSON_FILE_PATH = 'modified_date.json'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def change_date():
    data = {'date': datetime.now().strftime(DATE_FORMAT)}

    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)


def run_command(command):
    print(f"Running command: {' '.join(command)}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        stdout_line = process.stdout.readline()
        stderr_line = process.stderr.readline()

        if stdout_line == '' and stderr_line == '' and process.poll() is not None:
            break

        if stdout_line:
            print(f"STDOUT: {stdout_line.strip()}")

        if stderr_line:
            print(f"STDERR: {stderr_line.strip()}")

    # Wait for the process to complete
    process.wait()

    if process.returncode != 0:
        print(f"Command failed with return code {process.returncode}")

    print("\n")


def get_container_ids_by_tag(tag, server_address=None):
    if server_address:
        command = ["ssh", server_address, "docker", "ps", "-a", "--filter", f"ancestor={tag}", "--format", "{{.ID}}"]
    else:
        command = ["docker", "ps", "-a", "--filter", f"ancestor={tag}", "--format", "{{.ID}}"]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )

        container_ids = result.stdout.strip().split('\n')
        return container_ids

    except subprocess.CalledProcessError as e:
        print("Error running docker command:", e)
        return []


def get_image_ids_by_tag(tag, server_address=None):
    if server_address:
        command = ["ssh", server_address, "docker", "images", "phanytale:latest", "-q"]
    else:
        command = ["docker", "images", "phanytale:latest", "-q"]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )

        image_ids = result.stdout.strip().split('\n')
        return image_ids

    except subprocess.CalledProcessError as e:
        print("Error running docker command:", e)
        return []


change_date()
local_container_ids = get_container_ids_by_tag("phanytale:latest")
server_container_ids = get_container_ids_by_tag("phanytale:latest", server_address=SERVER_ADDRESS)
local_image_ids = get_image_ids_by_tag("phanytale:latest")
server_image_ids = get_image_ids_by_tag("phanytale:latest", server_address=SERVER_ADDRESS)

# Stop running containers
if local_container_ids != ['']:
    run_command(["docker", "stop"] + local_container_ids)
if server_container_ids != ['']:
    run_command(["ssh", "nucubuntunl", "docker", "stop"] + server_container_ids)

# Remove stopped containers
if local_container_ids != ['']:
    run_command(["docker", "rm"] + local_container_ids)
if server_container_ids != ['']:
    run_command(["ssh", "nucubuntunl", "docker", "rm"] + server_container_ids)

# Delete images
if local_image_ids != ['']:
    run_command(["docker", "rmi", "-f"] + local_image_ids)
if server_image_ids != ['']:
    run_command(["ssh", "nucubuntunl", "docker", "rmi", "-f", "phanytale:latest"])

# Build the image
run_command(["docker", "build", "-t", "phanytale:latest", "."])

# Tag the image with the GCR name
run_command(["docker", "tag", "phanytale:latest", "phanytale:v1.0"])

# Push to the Container Registry
run_command(["docker", "save", "-o", "/home/ample/phanytale.tar", "phanytale:latest"])

# Deploy the image to Cloud Run
run_command(["scp", "/home/ample/phanytale.tar", "nucubuntunl:/home/ample/"])

# Delete the tar file from the local machine
run_command(["rm", "/home/ample/phanytale.tar"])

# Run the load command remotely
run_command(["ssh", "nucubuntunl", "docker", "load", "-i", "/home/ample/phanytale.tar"])

# Run the container
run_command(["ssh", "nucubuntunl", "sudo", "docker", "run", "--name", "phanytale_api", "-d", "-p", SERVER_PORT+":"+SERVER_PORT, "phanytale:latest"])

# List the docker images
run_command(["docker", "images"])
run_command(["ssh", "nucubuntunl", "docker", "images"])
