#pylint: disable=line-too-long
import sys
import traceback
import datetime
import boto3
import botocore
from pathlib import Path
import logging
from typing import Generator

from multiprocessing.pool import ThreadPool
from legopython import lp_logging, lp_general, lp_awssession

'''
S3

 module to interact with AWS S3.

Examples:

        $ S3 file.txt s3:\\file-prod\prod
        $ S3 s3:\\file-prod\prod\Downloads
'''

AWS_REGION = 'us-east-1'

s3 = boto3.resource('s3')
s3c = boto3.client('s3', config=botocore.client.Config(max_pool_connections=200))

logger = logging.getLogger("python")


def s3url_cleaner(s3url:str) -> str:
    '''
    s3url_cleaner -- take an S3 URL and clean it up by removing the s3:// portion
        s3url - s3url to clean

    return - string
    '''
    if s3url[0:5].lower() == "s3://" :
        return s3url[5:]
    return s3url


def return_s3bucket(s3url:str):
    '''
    return_s3bucket - Return an S3 bucket object
        s3url - S3 url (with or without s3://) to parse

    return - S3 Bucket
    '''
    spliturl = s3url_cleaner(s3url).split('/') #[0] is the bucket, [1:] is the key
    return s3.Bucket(spliturl[0])


def return_s3path(s3url) :
    '''
    return_s3path - Return the S3 key
    s3url - S3 url (with or without s3://) to parse
    return - string
    '''
    spliturl = s3url_cleaner(s3url).split('/') #[0] is the bucket, [1:] is the key
    if len(spliturl) == 1 :
        return "" #No path was specified, so we're uploading to the top-level of the bucket
    return "/".join(spliturl[1:])# + "/" -- NOTE -- there will be a trailing blank item when s3url.split runs ['blah','blah,''] , which will add the trailing slash in


def return_s3filename(s3url) :
    '''
    return_s3filename - Return the filename for the given s3url
        s3url - S3 url to parse

    Return: Returns nothing if this is a file, otherwise the filename from the key.
    '''
    if len(s3url_cleaner(s3url).rsplit('/', 1)) == 1 : #for files in the top-level "folder"
        return s3url_cleaner(s3url)
    return s3url_cleaner(s3url).rsplit('/', 1)[1]


def return_s3folderpath(key, bucket=True) :
    '''
    Return the file path for the given key or S3url
        key - key to parse folder path from
        bucket - True = strip bucket from key; False = don't strip bucket
            #TODO - bucket parameter is a stop gap - this function should be deprecated in place of a v2 function that
            #actually uses a key and won't work on s3urls as this function has accidentally been doing

    Return: Returns string filepath
    '''
    key = s3url_cleaner(key)
    # if s3url_cleaner(key) != key : #don't return the bucket in the folder path
    if len(key.split('/')) <= 2 :#files are in the top level
        return '/' #TODO - should this return a "/"?
        #everything else, strip out the bucket name and add the trailing slash back in
    if bucket:
        return key.rsplit('/', 1)[0].split('/',1)[1] + '/'
    return key.rsplit('/', 1)[0] + '/'
    # elif len(key.split('/')) == 1 : #deal with keys passed in at the top level
    #     return '' #TODO - should this return a "/"?
    # else :
        # return key.rsplit('/', 1)[0] + '/' #rsplit strips the trailing slash, add back in


def __getAS3File(bucket, key, downloadfolder = '.', delete = False, fileLedger = None, contents = False) :
    '''
    #TODO - Deal with the fileLedger better for return of object contents, so it's not just the localfolder
    '''
    try:
        logger.info("Function getAS3Files - Trying to download " + bucket.name + "/" + key)
        # s3c.download_file(bucket.name, key, downloadfolder + '/' + key.split('/')[-1])
        # logger.info("Function getAS3Files - " + bucket.name + "/" + key + " downloaded successfully")

        s3obj = s3c.get_object(
                Bucket=bucket.name,
                Key=key
        )

        if fileLedger : #TODO - this should be recorded here but run below the download_file in case the operation crashes
            lp_logging.writeToFileLedger(
                    return_s3filename(key),
                    's3://' + bucket.name + '/' + key,
                    Path(downloadfolder).resolve(), #Get the full path, not just the relative one passed in
                    (s3obj['LastModified'].replace(tzinfo=None) - datetime.datetime.utcfromtimestamp(0)).total_seconds(),
                    s3obj['ContentLength'],
                    fileledgerpath=fileLedger
                )

        logger.debug(f"Function getAS3File - {bucket.name} | {key} | {downloadfolder}'/'{key.split('/')[-1]}")
        if not contents :
            s3c.download_file(bucket.name, key, downloadfolder + '/' + key.split('/')[-1])
            logger.info("Function getAS3Files - " + bucket.name + "/" + key + " downloaded successfully")

        if delete :
            try:
                s3c.delete_object(
                    Bucket=bucket.name,
                    Key=key
                )
                logger.info("Function getAS3Files - " + bucket.name + "/" + key + " deleted successfully")
            except Exception as e:
                logger.error("Function getAS3Files - Deleting s3 object " + bucket.name + "/" + key + " failed with error " + str(e))
                traceback.print_exc()

        if contents :
            return s3obj['Body'].read() #This might be problematic long-term, possibly just return the body and let the user stream it?
    except Exception as e:
        logger.error("Function getAS3Files - downloaded s3 object " + bucket.name + "/" + key + " failed with error " + str(e))
        traceback.print_exc()


def getS3Files(s3url, downloadfolder = '.', archive = False, delete = False, suffix = '', fileLedger = None, poolWorkers = 100, doFDWCallback = False) :
    '''Retrieve files from an S3 bucket. Specify an individual file, or a directory to download all files. Will not recurse into subdirectories.
        s3url - path to file(s) on S3 to retrieve
        downloadfolder (opt) - Local folder to download files to (default = current directory)
        suffix (opt) - Allow passing a suffix to filter files downloaded
        archive (opt) - True/False - move the file to an archive subdirectory once successfully downloaded (default = False)
        delete (opt) - True/False - delete the file from S3 once successfully downloaded (default = False)
        fileLedger (opt) - designed for s3same, captures details of files in a list of dictionaries
    '''
    logger.info(f'Downloading files from {s3url} to {downloadfolder}')
    logger.debug(f'Archive: {archive}|delete: {delete}|fileLedger: {fileLedger}|poolWorkers: {poolWorkers}')

    if delete and archive :
        logger.error("Cannot both delete and archive")
        traceback.print_exc()
        return False

    bucket = return_s3bucket(s3url)
    filecount = 0

    if poolWorkers > 1 : #if set to 1, skip multiprocessing
        pool = ThreadPool(poolWorkers)

    if not Path(downloadfolder).is_dir() :
        logger.error(f"Local path '{downloadfolder}' does not exist, unable to download files")
        traceback.print_exc()
        return False

    try :
        for key in listMatchingS3Keys(s3url, suffix = suffix) : #TODO -- support passing in s3delimeter to support recursion in this function
            if key.endswith('/') : #we'll get the folder in the results, which we don't want to download
                continue

            try :
                if poolWorkers > 1 :
                    pool.apply_async(__getAS3File, (bucket, key,), {'downloadfolder':downloadfolder, 'archive':archive, 'delete':delete, 'fileLedger':fileLedger, 'doFDWCallback':doFDWCallback})
                else :
                    __getAS3File(bucket, key, downloadfolder=downloadfolder, archive=archive, delete=delete, fileLedger=fileLedger, doFDWCallback=doFDWCallback)

                filecount += 1
            except KeyboardInterrupt :
                # Ctrl-C pressed
                logger.error("CTRL-C pressed ")
                if poolWorkers > 1 :
                    pool.close()
                    pool.join()  # Wait for all operations to finish
                return False
            except Exception as e:
                logger.error("Downloaded s3 object " + bucket.name + "/" + key + " failed with error " + str(e))
                traceback.print_exc()
                continue
    finally :
        if poolWorkers > 1 :
            pool.close()
            pool.join()  # Wait for all operations to finish
    if poolWorkers > 1 :
        if filecount > 0 :
            logger.info("Downloaded " + str(filecount) +" files from " + s3url + " to " + downloadfolder)
            logger.info('Waiting for all downloads to complete')
        pool.close()
        pool.join()  # Wait for all operations to finish

    if filecount > 0 :
        return True
    return False


def getS3FileContents(s3url, archive = False, delete = False, fileLedger = None):
    '''
    Return the contents of an S3 file, for use in either a file-like object or as the text of a file
    '''
    bucket = return_s3bucket(s3url)
    key = return_s3path(s3url)
    return __getAS3File(bucket, key, contents = True, archive=archive, delete=delete, fileLedger=fileLedger)


def sendAFileToS3(filepath, s3url, delete = False, bucket='', fileLedger = None) :
    '''
    sendAFileToS3 - mostly designed to be called by sendFilesToS3 to enabled multiprocessing,
    but can also be called for individual files to aid efficiency when parallelism is unneeded
        filepath - local filepath of file to send to S3
        s3url - S3 location to upload files (hint: this should end in '/')
        delete (opt) - True/False - delete the local file once successfully uploaded
        bucket (opt) - if a bucket object exists, pass it in to improve efficiency
        fileLedger (opt) - capture details of files moved in a fileledger, pass in path to turn on
    '''

    filepath = Path(filepath)
    if filepath.is_dir() : #can't upload a directory, so nothing to do
        return

    if bucket == '' :
        bucket = return_s3bucket(s3url)

    s3folderpath = return_s3path(s3url)
    try :
        s3c.upload_file(str(filepath), bucket.name, s3folderpath + filepath.name)
        logger.info("Function sendAFileToS3 - file " + str(filepath) + " uploaded successfully to " + s3url)
    except Exception as e :
        logger.error("uploading file " + str(filepath) + " to s3 location " + bucket.name + "/" + s3folderpath + " failed with error " + str(e))
        traceback.print_exc()

    if delete :
        try:
            filepath.unlink()
            logger.info('Function sendAFileToS3 - ' + str(filepath) + ' was deleted')
        except Exception as e:
            logger.error("Function sendAFileToS3 - Deleting file " + str(filepath) + " failed with error " + str(e))
            traceback.print_exc()


def sendFilesToS3(filepath, s3url, delete = False, poolWorkers = 100, fileLedger = None) :
    '''
    sendFilesToS3 - send a single file, file glob, or directory to and S3 location
        filepath - local filepath of file(s) to send to S3
        s3url - S3 location to upload files (hint: this should end in '/')
        delete (opt) - True/False - delete the local file once successfully uploaded
        archive (opt) - True/False - move the file into an archived directory once successfully uploaded
        poolWorkers (opt) - 1 - Number of pool workers to use, set to 1 to disable multithreading by default
        fileLedger (opt) - designed for s3same, captures details of files in a json fileledger
    '''
    #If we're archiving, validate the archived directory exists before proceeding

    if len(list(lp_general.listdir_path_v2(filepath))) == 0 :
        logger.warning("Function sendFilesToS3 sending files in " + filepath + " to " + s3url + " - No files in " + filepath)
        return

    logger.info("Function sendFilesToS3 - uploading files from " + filepath + " to " + s3url)
    bucket = return_s3bucket(s3url)
    filecount = 0
    if poolWorkers > 1 : #if set to 1, skip multiprocessing
        pool = ThreadPool(poolWorkers)

    try :
        for f in lp_general.listdir_path_v2(filepath) :
            #we can only send files, so make sure this isn't a directory
            if f.is_dir() :
                continue
            if poolWorkers > 1 :
                pool.apply_async(sendAFileToS3, (f, s3url, delete, bucket, fileLedger,))
            else :
                sendAFileToS3(f, s3url, delete, bucket, fileLedger)
            filecount += 1
    except KeyboardInterrupt :
        # Ctrl-C pressed
        pool.close()
        logger.info("Cancelling upload...")
        pool.join()  # Wait for all operations to finish
    if poolWorkers > 1 :
        if filecount > 0:
            logger.info('Function sendFilesToS3 waiting for all uploads to complete')
        pool.close()
        pool.join()  # Wait for all operations to finish


def copyFileInS3(s3urlfrom, s3urlto, delete=False, archive=False, rename = False) :
    '''
    copyFileInS3 - Copy a single file from one S3 location to another
    s3urlfrom (req) - S3 URL of keys to move
    s3urlto (req) - s3 folder URL of destination
    delete (opt)
    archive (opt)
    fdw_callback (opt) - perform a callback using FDW metadata in the s3 key to show file was delivered (as if it had gone through FDW)
    rename (opt) - s3urlto contains full s3 path and filename
    
    TODO - This function should support a "rename" mode where the s3urlto us used literally as the destination and not the folder location
    '''
    if delete and archive :
        logger.error("Function copyFileInS3 - Cannot both delete and archive")
        return

    bucket_from = return_s3bucket(s3urlfrom)
    bucket_to = return_s3bucket(s3urlto)

    s3folderpath_from = return_s3folderpath(s3urlfrom)
    s3folderpath_to = return_s3folderpath(s3urlto)
    
    s3filename_from = return_s3filename(s3urlfrom)
    
    if rename: #the filename is in the s3urlto URL string, so don't use the one in the s3urlFROM string
        if s3urlto[-1] == '/':
            logger.error('Cannot rename file, as destination does not contain a filename')
            return
            #TODO - this should thrown an exception instead of just returning
        s3filename_to = return_s3filename(s3urlto)
    else:
        s3filename_to = s3filename_from

    logger.debug(f'From -> bucket_from: {bucket_from} | s3folderpath_from: {s3folderpath_from} | filename: {s3filename_from}')
    logger.debug(f'To -> bucket_to: {bucket_to} | s3folderpath_to: {s3folderpath_to} | filename: {s3filename_to}')
    s3c.copy( { 'Bucket' : bucket_from.name, 'Key': s3folderpath_from + s3filename_from}, bucket_to.name, s3folderpath_to + s3filename_to)
    #bucket_to.copy( { 'Bucket' : bucket_from.name, 'Key': s3folderpath_from }, s3folderpath_to + return_s3filename(s3urlfrom))
    if delete :
        logger.debug(f'Deleting object {bucket_from.name}/{s3folderpath_from}{s3filename_from}')
        s3c.delete_object(
            Bucket=bucket_from.name,
            Key=s3folderpath_from + s3filename_from
        )
    logger.info(f'successfully copied {s3urlfrom} to {s3urlto}')


def copyFilesInS3(s3urlfrom, s3urlto, suffix='', delete=False, archive=False, poolWorkers = 150, limit = 0, fdw_callback = False) :
    '''
    copyFilesInS3 - Copy a set of files from one S3 location to another
    s3urlfrom (req) - S3 URL of keys to move
    s3urlto (req) - s3 URL of destination
    suffix (opt) - Only copy files with specific suffix
    delete (opt) - Default: False - Delete the source file after copying
    archive (opt) - Default: False - Archive the source file after copying
    poolWorkers (opt) - Default: 100 - Number of threads to use to speed up copying
    limit (opt) - Default: none - Number of files to move before returning
    '''
    logger.debug(f'Function copyFilesInS3 - archive: {archive}|delete: {delete}|poolWorkers: {poolWorkers}|limit: {limit}')
    if delete and archive :
        logger.error("Function copyFilesInS3 - Cannot both delete and archive")
        return
    logger.info("Function copyFilesInS3 - copying files from " + s3urlfrom + " to " + s3urlto)

    if (s3urlfrom != s3urlto) and (s3urlto[-1] != '/') :
        logger.error("Function copyFilesInS3 - s3url destination needs to match s3urlfrom or represent a folder '/'")
        return

    if poolWorkers > 1 : #if set to 1, skip multiprocessing
        pool = ThreadPool(poolWorkers)

    count = 0
    try :
        bucket_from = return_s3bucket(s3urlfrom)
        for key in listMatchingS3Keys(s3urlfrom, suffix) :
            if poolWorkers > 1 :
                logger.debug(f'copyFilesInS3 - delivering {key} multi-processed')
                pool.apply_async(copyFileInS3, (bucket_from.name + '/' + key, s3urlto, delete, archive,), {'fdw_callback' : fdw_callback})
            else :
                logger.debug(f'copyFilesInS3 - delivering {key} serially')
                copyFileInS3(bucket_from.name + '/' + key, s3urlto, delete, archive, fdw_callback)
            count += 1
            if limit:
                if count >= limit :
                    break
    except KeyboardInterrupt :
        # Ctrl-C pressed
        logger.info("Cancelling copy...")
        if poolWorkers > 1 :
            pool.close()
            pool.join()  # Wait for all operations to finish
    if poolWorkers > 1 :
        pool.close()
        pool.join()  # Wait for all operations to finish


def write_file_to_S3(s3url, content):
    '''
    Writes a file directly to S3 without needing a file path.
    s3url: an S3 url of the flavor s3://bucket/some/path/to/key.ext
    content: the content that will be written to the file
    '''
    bucket = return_s3bucket(s3url)
    key = return_s3path(s3url)
    if isinstance(content,str):
        content = bytes(content.encode())
    s3c.put_object(Body=content,Bucket=bucket.name,Key=key)

def delete_key(bucket, key):
    '''
    TODO - This should be able to use either a Bucket object or a Bucket name (str)
    '''
    s3c.delete_object(Bucket = bucket,Key = key)

def object_key_exists(bucket,key):
    try:
        s3.Object(bucket,key).load() #grabs S3 object head if it exists as a fast check to see if it exists
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            #print (f"{bucket} {key} does not exist")
            return False
    else:
        #print (f"{bucket} {key} exists")
        return True


def listMatchingS3Keys(s3url: str, suffix='', returnObj = False, s3delimiter = '/') -> Generator :
    '''
    listMatchingS3Keys - Used to iterate/list a directory of contents in S3, will return either an S3 object or a string. Uses
                    a Boto3 paginator to return results for searches with more than 1,000 keys returned.
    s3url - S3 url where you want to return the list
    suffix (opt) - Only return entries which end with this, useful for returning only .zip or .pdf files (for example)
    returnObj (opt) - default = False - Instead of returning a string of the name, return an S3 object
    s3delimter (opt) - default = '/' - for use on buckets using delimiters outside the standard,
                    or also can be set to '' to aid in recursive searching of "sub folders"

    Returns - Default: string of the key name, Optionally: S3 Object of the key

    From: https://alexwlchan.net/2019/07/listing-s3-keys/
    * This function mashes together two functions from the above page, while maintaining the ability to return the S3 obj if desired.

    Generate objects in an S3 bucket.
    Example:

    for i in S3.listMatchingS3Keys('s3://s3-test/sftp/'):
        print(i)

    :param s3url: s3 URL to use to match files/keys
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional).
    :param returnObj: Return an s3 object instead of a string (optional)
    :param s3delimiter: delimiter used across "folders", at this is '/'
    '''
    bucket = return_s3bucket(s3url)
    s3folderpath = return_s3path(s3url)

    paginator = s3c.get_paginator("list_objects_v2")

    kwargs = {'Bucket':bucket.name, 'Prefix':s3folderpath, 'Delimiter':s3delimiter} #Set Delimiter to prevent sub-directories from being listed as well
    logger.debug(kwargs)
    for page in paginator.paginate(**kwargs):
        try:
            contents = page["Contents"]
        except KeyError:
            break

        for obj in contents:
            #Don't return keys that are folders
            if obj["Key"].endswith('/') :
                continue
            if obj["Key"].endswith(suffix):
                if returnObj :
                    yield obj
                else :
                    yield obj["Key"]


def listDirectories(s3url: str) -> dict:
    '''
    listDirectories - Return all the "subdirectories" at the given S3 URL level (but not recursively, just at that level)
       s3url - The S3 URL where you want to return the list of subdirectories

    Returns - directory object with 'prefix' being the name of the directory
    '''
    bucket = return_s3bucket(s3url)
    s3folderpath = return_s3path(s3url)

    if s3folderpath == '' :
        logger.debug('Calling this function at the top level is probably not what you wanted to do, and will take a long time to run for most S3 Buckets')

    paginator = boto3.client("s3").get_paginator("list_objects_v2")

    kwargs = {'Bucket': bucket.name, 'Prefix' : s3folderpath, 'Delimiter' : '/'} #Set Delimiter to prevent sub-directories from being listed as well
    logger.debug(kwargs)
    
    for page in paginator.paginate(**kwargs):
        logger.debug(page)
        if page.get('CommonPrefixes') is None:
            logger.debug('List of directories returned 0 results')
            return '' #return empty instead of None to prevent iterator exceptions with empty lists
        for object in page.get('CommonPrefixes'):
            yield object


def main() :
    import argparse
    if lp_awssession.checkSession() is False :
        logger.error('AWS Session is not valid, please renew token or check credentials')
        exit(1)
    #Import parameters (https://docs.python.org/3/library/argparse.html)
    parametersParser = argparse.ArgumentParser(description='Used to download or upload files for AWS S3')
    #All variations of S3 require two parameters, but they're different depending on what is being done, give them generic names
    parametersParser.add_argument('FirstArgument', help = '1st parameter needs to be either an S3URL, a single file, a directory, or a file glob')
    parametersParser.add_argument('SecondArgument', help = '2nd parameter can be either an S3URL, or a download location')
    #Add optional parameters as well
    parametersParser.add_argument('--delete', help = 'Delete file after processing', default = False, action="store_true") #Because this is deletion, don't give a short param for this
    parametersParser.add_argument('-a', '--archive', help = 'Move file to archive directory after processing', default = False, action="store_true")
    parametersParser.add_argument('-w', '--workers', help = 'For multi-threaded actions, how many workers to use', type=int, default=30)
    parametersParser.add_argument('-d', '--debug', help = 'Set logging to DEBUG to show debug log messages', default = False, action="store_true")
    parametersParser.add_argument('-l', '--ledger', help = 'store files in a file ledger in the current working directory', default = False, action="store_true")

    parameters = parametersParser.parse_args()

    lp_logging.MPAddHandler()

    if parameters.debug :
        lp_logging.MPDebugLogging()

    if parameters.ledger : #For easy coding, just store the fileledger in the local directory
        fileLedger = '.'
    else :
        fileLedger = None

    #See if we got an S3 URL explicitly for the first or second parameters, since this is cheap to check and very accurate for intention
    if parameters.FirstArgument[0:5].lower() == "s3://" :
        if parameters.SecondArgument[0:5].lower() == "s3://" : #First and second arguments are s3 URLs, so we know we're copying between S3 locs
            copyFilesInS3(parameters.FirstArgument, parameters.SecondArgument, delete=parameters.delete, archive=parameters.archive)
            sys.exit()
        suffix = ''
        if '*' in parameters.FirstArgument.rsplit('/', 1)[1] : #If the asterisk is anywhere else, don't accomodate that here
            suffix = parameters.FirstArgument.rsplit('/', 1)[1][1:] #Suffix can't include the asterisk, remove it with [1:]
            parameters.FirstArgument = parameters.FirstArgument.rsplit('/', 1)[0] + '/' #add the forward slash back in, as it's removed in the .split()
        getS3Files(parameters.FirstArgument, parameters.SecondArgument, delete=parameters.delete, archive=parameters.archive, suffix=suffix, fileLedger=fileLedger)
        sys.exit()
    elif parameters.SecondArgument[0:5].lower() == "s3://" :
        sendFilesToS3(parameters.FirstArgument, parameters.SecondArgument, delete=parameters.delete, archive=parameters.archive, poolWorkers=parameters.workers, fileLedger=fileLedger)
        sys.exit()

    FAPath = Path(parameters.FirstArgument) #Create a Path object to make checking the first 3 conditions easier
    if FAPath.is_dir() or FAPath.is_file() :
        sendFilesToS3(parameters.FirstArgument, parameters.SecondArgument, delete=parameters.delete, archive=parameters.archive, poolWorkers=parameters.workers, fileLedger=fileLedger)
    elif "*" in FAPath.name and len(list(Path(FAPath.parent).glob(FAPath.name))) > 0 : #rely on short-circuited AND to prevent the 2nd call from throwing an exeption
        sendFilesToS3(parameters.FirstArgument, parameters.SecondArgument, delete=parameters.delete, archive=parameters.archive, poolWorkers=parameters.workers, fileLedger=fileLedger)
    elif s3.meta.client.head_bucket(Bucket=parameters.SecondArgument.split('/')[0]) : #Do a small amount of due diligence to see if the S3 bucket actually exists #TODO - this throws an exception so we need to catch cleanly when a bucket doesn't exist
        #If there's an asterisk, turn this into a suffix for download
        suffix = ''
        if '*' in parameters.FirstArgument.rsplit('/', 1)[1] : #If the asterisk is anywhere else, don't accomodate that here
            suffix = parameters.FirstArgument.rsplit('/', 1)[1][1:] #Suffix can't include the asterisk, remove it with [1:]
            parameters.FirstArgument = parameters.FirstArgument.rsplit('/', 1)[0] + '/' #add the forward slash back in, as it's removed in the .split()
        getS3Files(parameters.FirstArgument, parameters.SecondArgument, delete=parameters.delete, archive=parameters.archive, suffix=suffix, fileLedger=fileLedger)
    else :
        logger.warning("we're unable to determine what to do with the parameters passed, please double check you've\npassed in either an S3 URL for an existing bucket, a directory, a file, or a fileglob as the first parameter")

if __name__ == '__main__':
    main()
