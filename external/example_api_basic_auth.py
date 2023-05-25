'''Example Basic Auth function to demonstrate legopython features.

Run this file to see how it will handle 
'''
from legopython import lp_api, lp_settings
from legopython.lp_logging import logger

#Env_config can be initialized by environment. An auth_handler is created for each environment. 
#Swapping between environments grabs saved creds.
env_config = {}
for env in ["prod", 'test']:
    env_config[env] = {"api_url": "https://www.reddit.com/"}

#If global envirnment setting is exists as an environment to use, create auth handler.
if lp_settings.ENVIRONMENT in list(env_config.keys()):
    auth_handler = lp_api.AuthHandler(
        name="reddit_basic",
        auth_type=lp_api.AuthType.BASIC,
        env_config=env_config,
        env=lp_settings.ENVIRONMENT
    )
    manage_auth = auth_handler.manage_auth
else:
    logger.warning(f'example_api_basic_auth.py will not be able to make calls since {lp_settings.ENVIRONMENT} is not a support environment')


@manage_auth
def ping_reddit_api_page(**kwargs):
    '''Here is an example of how auth and environment is passed through a function.'''
    #Note: This example doesn't need auth
    return lp_api.send_http_call(
        method='get',
        url=f"{(kwargs.get('api_url'))}",
        headers = {**{'Content-Type': 'application/json'}, **kwargs.get('headers')},
        print_request = True
        )

def main():
    '''Run a test against reddit'''
    result = ping_reddit_api_page()
    print(result)

if __name__ == '__main__':
    main()
