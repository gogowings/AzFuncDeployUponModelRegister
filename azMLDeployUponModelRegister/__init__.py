import json
import logging
import os

import azure.functions as func
from azureml.core import Workspace, Model, Environment
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.model import InferenceConfig
from azureml.core.webservice.aci import AciServiceDeploymentConfiguration

def main(event: func.EventGridEvent):
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    logging.info('Python EventGrid trigger processed an event: %s', result)

    # get service principal from env variables
    sp_auth = ServicePrincipalAuthentication(
        tenant_id=os.getenv('TENANT_ID', ''),
        service_principal_id=os.getenv('SP_ID', ''),
        service_principal_password=os.getenv('SP_PASSWORD', ''))
    
    # get workspace
    ws = Workspace.get(
        name=os.getenv('WORKSPACE_NAME', ''),
        auth=sp_auth,
        subscription_id=os.getenv('SUBSCRIPTION_ID', ''),
        resource_group=os.getenv('RESOURCE_GROUP', ''))

    logging.info(
        'SubscriptionID = %s; ResourceGroup = %s; WorkSpace = %s; Location = %s',
        ws.subscription_id,
        ws.resource_group,
        ws.name,
        ws.location)
    
    # get model from event data
    event_data = event.get_json()
    model_id = '{}:{}'.format(event_data['modelName'], event_data['modelVersion'])
    model = Model(ws, id=model_id)
    logging.info('Model name = %s', model.name)

    # deploy
    env = Environment.from_conda_specification('aci-test-env', './Inference/env.yml')
    registered_env = env.register(ws)

    inference_config = InferenceConfig('./Inference/score.py', environment=registered_env)

    aci_config = AciServiceDeploymentConfiguration(cpu_cores=1, memory_gb=2)

    service_name = 'acitest-{}-{}'.format(event_data['modelName'], event_data['modelVersion'])
    service = Model.deploy(ws, service_name, [model], inference_config, aci_config)
    logging.info('Deploying service %s to ACI', service.name)

    service.wait_for_deployment(True)
    logging.info('Deployment completed.')





