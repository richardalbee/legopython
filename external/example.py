#pylint: disable=line-too-long, consider-using-dict-items, no-value-for-parameter
'''
Function to interact with Camunda for Python.
'''
import boto3
from legopython import lp_api, lp_awssession, lp_settings, lp_secretsmanager
from legopython.lp_logging import logger

kms_client = boto3.client('kms')

APP_BASE_URL = "https://application.com"
env_config = {
    "test": {
        "token_params":
            {"url": "https://application.dev.com/oauth/token"},
        "api_url": "https://test-application.com/api/"
    },
    "prod": {
        "token_params":
            {"url": "https://application.us.auth0.com/oauth/token"},
        "api_url": "https://application.com/api/"
    }
}

if not lp_awssession.checkSession():
    logger.error("Authenticate using your AWS credentials to proceed.")

for environment in env_config.keys():
    env_config[environment]["token_params"]["data"] = {
        "audience": "https://application.health.com",
        "grant_type": "client_credentials",
        **(lp_secretsmanager.get_secret_v2(f"{environment}-auth0-application-client"))
    }
    env_config[environment]["token_params"]["headers"] = {"Content-Type":"application/x-www-form-urlencoded"}

auth_handler = lp_api.AuthHandler(
    name="example",
    auth_type=lp_api.AuthType.JWT_BEARER,
    env_config=env_config,
    env=lp_settings.ENVIRONMENT
)
manage_auth = auth_handler.manage_auth


@manage_auth()
def auth_example(**kwargs):
    '''Here is an example of how auth and environment is passed through a function.'''

    input_headers = kwargs.get('headers')
    input_headers['Content-Type'] = 'application/json'
    lp_api.get_api_json(
        url=f"{(kwargs.get('api_url',APP_BASE_URL))}/rest/api",
            data = [],
            headers = input_headers,
            print_json = True
        )
    print(kwargs)

print('TESTING EXAMPLE.py')
logger.info('example')
