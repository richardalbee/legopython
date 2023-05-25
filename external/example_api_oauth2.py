#pylint: disable=line-too-long, consider-using-dict-items, no-value-for-parameter, consider-iterating-dictionary, logging-fstring-interpolation
'''
Function to interact with restful-booker in Python.
Reddit oauth2 example: https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example
'''
from legopython import lp_api, lp_settings#, lp_secretsmanager
from legopython.lp_logging import logger
from requests.auth import HTTPBasicAuth

'''
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
'''
env_config = {}
for env in ["prod"]:
    env_config[env] = {"api_url": "https://www.reddit.com/"}



#If global envirnment setting is exists as an environment to use, create auth handler.
if lp_settings.ENVIRONMENT in list(env_config.keys()):
    auth_handler = lp_api.AuthHandler(
        name="reddit_oauth2",
        auth_type=lp_api.AuthType.BASIC,
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
app_client_id: s2U6_4wqGzD6OyEiiVXLig
app_client_secret: c6RonjocdVxrDZRZY6Jpj6avnCQCew  #https://www.reddit.com/prefs/apps
#https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example
'''

auth=HTTPBasicAuth('OH5G8Hldzay3sdITzHdw3w', '5htKDJ6wvuEwoe3_MkF3yLmFm4oCjQ')

@manage_auth
def get_new_token(**kwargs):
    return lp_api.send_http_call(
        method='post',
        url='https://www.reddit.com/api/v1/access_token',
        #auth = kwargs.get('headers'),
        headers = {**kwargs.get('headers'),**{"User-Agent": "ChangeMeClient/0.1 by python_test2_oauth2"}},
        data = {**{"grant_type": "password"}, **kwargs.get('headers')},
        auth=HTTPBasicAuth('OH5G8Hldzay3sdITzHdw3w', '5htKDJ6wvuEwoe3_MkF3yLmFm4oCjQ'),
        print_request = True
        )

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
    print(type(get_new_token))
    #result = get_new_token()
    #print(result)
    #print(result.text)

if __name__ == '__main__':
    main()
