#pylint: disable=line-too-long, consider-using-dict-items, no-value-for-parameter, consider-iterating-dictionary, logging-fstring-interpolation
'''
Function to interact with restful-booker in Python.
Reddit oauth2 example: https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example
'''
from legopython import lp_api, lp_settings#, lp_secretsmanager
from legopython.lp_logging import logger

env_config = {
    "test": {
        "token_params":
            {"url": "https://www.reddit.com"},
        "api_url": "https://oauth.reddit.com/api/v1"
    },
    "prod": {
        "token_params":
            {"url": "https://www.reddit.com"},
        "api_url": "https://oauth.reddit.com/api/v1"
    }
}

for env in env_config.keys():
    env_config[env]["token_params"]["data"] = {
        "audience": "https://configportal.moxehealth.com",
        "grant_type": "client_credentials",
        #**{} #TODO: Get example of this
        #**(lp_secretsmanager.get_secret(f"{env}-auth0-support-config-service-client"))
    }
    env_config[env]["token_params"]["headers"] = {"Content-Type":"application/x-www-form-urlencoded"}

#If global envirnment setting is exists as an environment to use, create auth handler.
if lp_settings.ENVIRONMENT in list(env_config.keys()):
    auth_handler = lp_api.AuthHandler(
        name="reddit_oauth2",
        auth_type=lp_api.AuthType.OAUTH2,
        env_config=env_config,
        env=lp_settings.ENVIRONMENT
    )
    manage_auth = auth_handler.manage_auth
else:
    logger.warning(f'Example.py will not be able to make calls since {lp_settings.ENVIRONMENT} is not a support environment')


'''
Reddit Example
username: python_test2_oauth2
password: oauth2_password_test
app_client_id: PPqLrZIO6lvSgeKnAlAdaw
app_client_secret: nzPTOK6PIRi7w0ZAnszArRfUvOqrhg  #https://www.reddit.com/prefs/apps
#https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example
'''
@manage_auth
def reddit_get_oauth2_bearer(**kwargs):
    ''''''
    result = lp_api.send_http_call(
        method='post',
        url=f"{(kwargs.get('api_url'))}/me",
        data = {"grant_type": "password", "username": "python_test2_oauth2", "password": "oauth2_password_test"},
        headers = {"User-Agent": "ChangeMeClient/0.1 by python_test2_oauth2"},
        print_request = True #Used to show the raw request being sent
        )
    print(result.json())


@manage_auth
def reddit_me_api(**kwargs):
    '''Here is an example of how auth and environment is passed through a function.'''

    return lp_api.send_http_call(
        method='get',
        url=f"{(kwargs.get('api_url'))}/me",
        headers = {"Authorization": "bearer fhTdafZI-0ClEzzYORfBSCR7x3M", "User-Agent": "ChangeMeClient/0.1 by python_test2_oauth2"},
        print_request = True #Used to show the raw request being sent
        )

def main():
    '''Run a test against the weather api'''
    result = reddit_me_api()
    print(result)

if __name__ == '__main__':
    main()
