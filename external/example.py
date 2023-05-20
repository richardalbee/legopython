#pylint: disable=line-too-long, consider-using-dict-items, no-value-for-parameter, consider-iterating-dictionary, logging-fstring-interpolation
'''
Function to interact with Camunda for Python.
'''
#import boto3
from legopython import lp_api, lp_settings#, lp_secretsmanager

#kms_client = boto3.client('kms')

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

for environment in env_config.keys():
    env_config[environment]["token_params"]["data"] = {
        "audience": "https://application.health.com",
        "grant_type": "client_credentials",
        #**(lp_secretsmanager.get_secret(f"{environment}-auth0-application-client"))
    }
    env_config[environment]["token_params"]["headers"] = {"Content-Type":"application/x-www-form-urlencoded"}

auth_handler = lp_api.AuthHandler(
    name="example",
    auth_type=lp_api.AuthType.BASIC,
    env_config=env_config,
    env=lp_settings.ENVIRONMENT
)
manage_auth = auth_handler.manage_auth


#@manage_auth()
def auth_example(**kwargs):
    '''Here is an example of how auth and environment is passed through a function.'''

    input_headers = kwargs.get('headers')
    input_headers['Content-Type'] = 'application/json'
    lp_api.send_http_call(
        method='get',
        url=f"{(kwargs.get('api_url',APP_BASE_URL))}/rest/api",
            data = [],
            headers = input_headers,
            print_json = True
        )
    print(kwargs)
