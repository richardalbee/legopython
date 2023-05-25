'''Module with base AWS functions relating to IAM permissions

To install AWS SSO Login:

Prerequisites
Download AWSCLI v2

Initial setup
Open terminal session and execute the following:

aws configure sso:
    If prompted for a SSO start URL, sign into AWS and find your SSO Start URL.
    For SSO Region just hit <enter> After the initial configuration, these values should be cached as the default and replace the [None] below.

Example Prompts:
    SSO session name (Recommended):
    SSO start URL [None]: {SSO Start URL}
    SSO Region [None]: us-east-2
'''
import os
import botocore.exceptions as bexcept
import boto3
from legopython.lp_logging import logger


def check_session() -> bool:
    '''Validates whether configured AWS session(s) are valid.'''
    #We are ASSUMING the user has a default AWS profile able to get the list of profile.
    session = boto3.Session()
    profiles = session.available_profiles

    for profile in profiles:
        session = boto3.Session(profile_name=profile, region_name='us-east-2')
        sts = session.client('sts')
        try:
            account = sts.get_caller_identity()['Account']
            logger.info(f'{profile}, {account}')
        except bexcept.NoCredentialsError:
            logger.warning(f'{profile},--- no credentials --')
            return False
        except bexcept.InvalidConfigError:
            logger.warning(f'{profile},--- invalid config --')
            return False
        except Exception as exc:
            logger.warning(f'{profile},--- exception --: {exc}')
            return False
        logger.debug('Found valid aws session in lp_awssession.')
        return True


def set_sso_profile() -> boto3.session.Session:
    '''Sets credentials for the AWS session based on environment variables:
    - If PYTHON_ROLE_ARN is set, the session attempts to assume a role
    - If PYTHON_AWS_PROFILE is set, it uses that AWS profile
    - If neither are set, then it uses default profile
    '''
    if os.environ.get('PYTHON_ROLE_ARN',False):
        sts = boto3.client('sts')
        sts_creds = sts.assume_role(
            RoleArn = os.environ['PYTHON_ROLE_ARN'],
            RoleSessionName = 'assumed_role'
        ).get('Credentials',False)
        if sts_creds:
            return boto3.Session(
                aws_access_key_id=sts_creds['AccessKeyId'],
                aws_secret_access_key=sts_creds['SecretAccessKey'],
                aws_session_token=sts_creds['SessionToken']
            )
    return boto3.Session(profile_name=next(x for x in (
        os.environ.get('PYTHON_AWS_PROFILE',None),
        'default'
    ) if x is not None))


class AWSTokenExpiredError(Exception):
    '''Exception raised for a failed token'''
    def __init__(self,message="AWS token is expired. Please refresh your token or session."):
        self.message = message
        super().__init__(self.message)


def main() :
    '''Quick token check!'''
    if check_session():
        print('AWS token is valid and not expired')


if __name__ == '__main__':
    main()
