#pylint: disable=line-too-long
'''
Function to interact with Camunda for Python.
'''
import base64
import json
from typing import Union,Sequence
import ast
import boto3
from Python import API, Secrets, AWS, Py, Settings
from Python.Logging import logger,cloudlog
from Python.API import InvalidStatusReturned

kms_client = boto3.client('kms')

APP_BASE_URL = "https://application.com"

env_config = {
    "test": {
        "token_params":
            {"url": "https://application.dev.com/oauth/token"},
        "api_url": "https://test-application.com/api/"
    },
    "int": {
        "token_params":
            {"url": "https://application.int.us.auth0.com/oauth/token"},
        "api_url": "https://int-application.com/api/"
    },
    "prod": {
        "token_params":
            {"url": "https://application.us.auth0.com/oauth/token"},
        "api_url": "https://application.com/api/"
    }
}

if not AWS.checkSession():
    logger.error("Authenticate using your AWS credentials to proceed.")

for env in env_config.keys():
    env_config[env]["token_params"]["data"] = {
        "audience": "https://application.health.com",
        "grant_type": "client_credentials",
        **(Secrets.get_secret_v2(f"{env}-auth0-application-client"))
    }
    env_config[env]["token_params"]["headers"] = {"Content-Type":"application/x-www-form-urlencoded"}

auth_handler = API.AuthHandler(
    name="example",
    auth_type=API.AuthType.JWT_BEARER,
    env_config=env_config,
    env=Settings.ENVIRONMENT
)

manage_auth = auth_handler.manage_auth


@manage_auth()
def fake_example(**kwargs):
    print(kwargs)