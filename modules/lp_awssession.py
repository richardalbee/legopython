'''Module with base AWS functions relating to IAM permissions'''
import boto3
import os
import logging

logger = logging.getLogger("pythontools")

def checkSession() -> bool:
    '''validates whether or not the user has a valid session'''
    try :
        boto3.client('sts').get_caller_identity()
    except :
        logger.warning("AWS Session invalid, or other issue connecting to AWS, please check your AWS session and network connectivity")
        return False
    logger.debug('awssession.checkSession found a valid session')
    return True


def set_sso_profile() -> boto3.session.Session:
    '''
    Sets credentials for the AWS session based on environment variables:
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
    if checkSession() :#todo -- add optional parameter to checkSession to give the time of token expiration
        logger.info('AWS token or session is valid and not expired')

if __name__ == '__main__':
    main()
