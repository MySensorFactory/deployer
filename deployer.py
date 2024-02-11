import os
from typing import Any

from pythoncommons.cicd_tools import SqsClient, S3Client, ParameterStoreClient, DeployConfig, KubernetesManager, YamlLoader


def rm_deploy_files(current_dir: str, config: DeployConfig):
    for filename in config.order:
        file_path = os.path.join(current_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def deploy(k8s_manager: KubernetesManager, deploy_config: DeployConfig):
    is_rollback_performed = False
    for manifest in deploy_config.order:
        if not is_rollback_performed:
            k8s_manager.perform_rollback_from_config_file('rollback.yml')
            is_rollback_performed = True
        k8s_manager.create_manifest(yaml_file=manifest)


def deploy_loop(current_dir: str,
                k8s_manager: KubernetesManager,
                s3client: Any,
                sqs_client: Any,
                yaml_loader: YamlLoader) -> None:
    while True:
        event = sqs_client.wait_for_event('Deploy')
        print('Got deploy event')

        s3_dir = event.value.config_dir

        print('Downloading ...')
        s3client.download_files_from_dir(
            s3_folder_path=s3_dir,
            local_folder=current_dir
        )

        print('Deploying ...')
        deploy_config = yaml_loader.parse_yaml('config.yml', DeployConfig)
        deploy(k8s_manager, deploy_config)
        rm_deploy_files(current_dir, deploy_config)


def main() -> None:
    BUCKET_NAME = 'factory-ci-cd'
    REGION = "eu-central-1"
    CICD_PARAMETER_QUEUE_URL_PARAM = "/CICD/CICDQueueUrl"

    k8s_manager = KubernetesManager()
    yaml_loader = YamlLoader()
    current_dir = os.getcwd()

    parameter_store_client = ParameterStoreClient(REGION)
    sqs_queue_url = parameter_store_client.get_parameter(CICD_PARAMETER_QUEUE_URL_PARAM)

    sqs_client = SqsClient(
        region=REGION,
        timeout=5,
        queue_url=sqs_queue_url
    )
    s3client = S3Client(
        region=REGION,
        bucket_name=BUCKET_NAME
    )

    deploy_loop(current_dir, k8s_manager, s3client, sqs_client, yaml_loader)


if __name__ == '__main__':
    main()
