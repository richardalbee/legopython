#pylint: disable=line-too-long
'''
Function to interact with Camunda for Python.
'''
import boto3
from legopython import lp_api, lp_aws, lp_settings, lp_logging, lp_secretsmanager, lp_settings

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

if not lp_aws.checkSession():
    lp_logging.error("Authenticate using your AWS credentials to proceed.")

for env in env_config.keys():
    env_config[env]["token_params"]["data"] = {
        "audience": "https://application.health.com",
        "grant_type": "client_credentials",
        **(lp_secretsmanager.get_secret_v2(f"{env}-auth0-application-client"))
    }
    env_config[env]["token_params"]["headers"] = {"Content-Type":"application/x-www-form-urlencoded"}

auth_handler = lp_api.AuthHandler(
    name="example",
    auth_type=lp_api.AuthType.JWT_BEARER,
    env_config=env_config,
    env=lp_settings.ENVIRONMENT
)

manage_auth = auth_handler.manage_auth


@manage_auth()
def fake_example(**kwargs):
    print(kwargs)

print('TESTING EXAMPLE.py')
