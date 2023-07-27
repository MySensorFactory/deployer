import os
import sys

import boto3
import kubernetes.client.exceptions
import yaml
from kubernetes import client, config


def create_deployment(namespace: str, manifest_path: str):
    load_kubernetes_config()
    manifest_file = load_manifest_file(manifest_path)
    api_instance = get_api_instance(manifest_file)

    try:
        api_instance.replace_namespaced_deployment(
            name=manifest_file['metadata']['name'],
            namespace=namespace,
            body=manifest_file
        )
        print("Service has been created")
    except kubernetes.client.exceptions.ApiException as e:
        print(f"Replacing service error code: {e.status}")
        if is_resource_missing(e):
            try:
                print("Service not found, creating ...")
                api_instance.create_namespaced_deployment(
                    namespace=namespace,
                    body=manifest_file
                )
            except kubernetes.client.exceptions.ApiException as e:
                print(f"Api exception: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


def create_service(namespace: str, manifest_path: str):
    load_kubernetes_config()
    manifest_file = load_manifest_file(manifest_path)
    api_instance = get_api_instance(manifest_file)

    try:
        api_instance.replace_namespaced_service(
            name=manifest_file['metadata']['name'],
            namespace=namespace,
            body=manifest_file
        )
        print("Service has been created")
    except kubernetes.client.exceptions.ApiException as e:
        print(f"Replacing service error code: {e.status}")
        if is_resource_missing(e):
            try:
                print("Service not found, creating ...")
                api_instance.create_namespaced_service(
                    namespace=namespace,
                    body=manifest_file
                )
            except kubernetes.client.exceptions.ApiException as e:
                print(f"Api exception: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
        else:
            print(f"Unexpected error: {str(e)}")

    except Exception as e:
        print(f"Unexpected error: {e}")


def create_ingress(namespace: str, manifest_path: str):
    load_kubernetes_config()
    manifest_file = load_manifest_file(manifest_path)
    api_instance = get_api_instance(manifest_file)

    try:
        api_instance.replace_namespaced_ingress(
            name=manifest_file['metadata']['name'],
            namespace=namespace,
            body=manifest_file
        )
        print("Ingress has been created")
    except kubernetes.client.exceptions.ApiException as e:
        print(f"Replacing ingress error code: {e.status}")
        if is_resource_missing(e):
            try:
                print("Ingress not found, creating ...")
                api_instance.create_namespaced_ingress(
                    namespace=namespace,
                    body=manifest_file
                )
            except kubernetes.client.exceptions.ApiException as e:
                print(f"Api exception: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
        else:
            print(f"Unexpected error: {str(e)}")

    except Exception as e:
        print(f"Unexpected error: {e}")


def is_resource_missing(e):
    return e.status == 404


def load_manifest_file(manifest_path):
    with open(manifest_path) as file:
        manifest_file = yaml.safe_load(file)
    return manifest_file


def load_kubernetes_config():
    config.load_kube_config()


apis = {
    "Deployment": client.AppsV1Api,
    "Service": client.CoreV1Api,
    "Ingress": client.NetworkingV1Api
}


def get_api_instance(manifest_file):
    return apis[get_manifest_kind(manifest_file)](client.ApiClient())


def get_manifest_kind(manifest):
    try:
        return manifest.get('kind', '')
    except KeyError as e:
        print(f"Unknown type of Kubernetes manifest, details:  {str(e)}")
        raise Exception()


def get_namespace(manifest):
    return manifest.get('metadata', {}).get('namespace', 'default')


def download_file_from_s3(bucket_name, file_key, destination_path):
    s3_client = boto3.client('s3')

    try:
        s3_client.download_file(bucket_name, file_key, destination_path)
        print(f"File {destination_path + file_key} has been downloaded.")
    except Exception as e:
        print(f"Cannot download file {destination_path + file_key} from S3: {str(e)}")


def parse_args(args):
    arg_map = {}
    key = None
    for arg in args:
        if arg.startswith("--"):
            key = arg[2:]
            arg_map[key] = None
        elif key:
            arg_map[key] = arg
            key = None
    return arg_map


def apply_manifests():
    args: dict = parse_args(sys.argv[1:])

    namespace = args['namespace']
    config_path = args['config_path']
    bucket_name = args['bucket_name']

    download_file_from_s3(bucket_name, f'{config_path}/ingress.yaml', 'ingress.yaml')
    download_file_from_s3(bucket_name, f'{config_path}/service.yaml', 'service.yaml')
    download_file_from_s3(bucket_name, f'{config_path}/deployment.yaml', 'deployment.yaml')

    create_deployment(namespace, 'deployment.yaml')
    create_service(namespace, 'service.yaml')
    create_ingress(namespace, 'ingress.yaml')

    print("Finished")


def rm_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename != "deployer.yaml":
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


# example of usage:
# python3 deployer.py --namespace factory-apps --config_path applications/demo1 --bucket_name factory-ci-cd
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Arguments not provided")
        exit(1)

    apply_manifests()
    rm_files("/")
