import subprocess
from docker import from_env
from docker.errors import DockerException
import json
import os

#Dictionary with the descriptions of the tests to display
descriptions = {
  "TC101": "Service Reachability",
  "TC201": "Basic Query",
  "TC301": "Single Remote Online Download",
  "TC102": "Test 2.1",
  "TC202": "Complex Query (Geo-Time Filter)",
  "TC302": "Multiple Remote Online Download"
}

def is_docker_running():
    try:
        client = from_env()
        client.ping()  # Attempts to ping the Docker daemon
        print("Docker is running.")
        return True
    except DockerException:
        print("Docker is not running.")
        return False

def run_command(command):
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(process.stdout.decode())
    return process

def check_container_exists(name):
    client = from_env()
    container_list = client.containers.list(all=True)
    for container in container_list:
        if name == container.name:
            return True
    return False

#Generate a results array from the json files to be rendered by the template
def generate_results(results_files):
    results = []

    for json_file in results_files:
        provider = json_file.split('-')[-2]
        if os.path.exists(json_file):
            with open(json_file, 'r') as file:
                data = json.load(file)
                for result in data.get('testCaseResults', []):
                    result['provider'] = provider
                    result['description'] = descriptions[result['testName']]
                    results.append(result)

    return results

def run_tests(container_name = "testsite-1", tests = ["TS01"], providers = ["cdse"], remove_container = True):

    #If docker is not running the returned false will trigger on app.py a redirection to /error/docker
    if not is_docker_running():
        return False 

    results_files = []

    for provider in providers:

        if not check_container_exists(container_name):
            print(f"Creating container {container_name}...")
            run_command(f"docker run --detach --name {container_name} ghcr.io/esacdab/cdab-testsuite:latest")
        else:
            print(f"Container {container_name} already exists. Continuing without creating a new one.")
            run_command(f"docker start {container_name}")

        run_command(f"docker cp config.yaml {container_name}:/home/jenkins/config.yaml")

        for test in tests:
            print(f"Executing {test} on {provider}...")
            run_command(f"docker exec {container_name} cdab-client -v -tsn={container_name} -tn={provider} {test}")

            result_file = f"{container_name}-{test}-{provider}-results.json"
            results_dir = os.path.join(os.path.dirname(__file__), 'Results')
            os.makedirs(results_dir, exist_ok=True)  # Creates the directory if it does not exist
            local_result_file = os.path.join(results_dir, result_file)
            print(f"Copying results for {test} from {provider}...")
            run_command(f"docker cp {container_name}:/home/jenkins/{test}Results.json {local_result_file}")
            results_files.append(local_result_file)
    
    if remove_container:
        print(f"Stopping and removing container {container_name}...")
        run_command(f"docker stop {container_name}")
        run_command(f"docker rm {container_name}")

    return generate_results(results_files)


if __name__ == "__main__":
    run_tests()
