from dotenv import load_dotenv
import os
import requests

# http://10.1.111.15:3666/http://10.1.111.7:31230/webhdfs/v1/usersapujagad/admingg/test?user.name=hdfs&op=MKDIRS

load_dotenv()

hdfs_url = os.getenv('HDFS_URL')

def mkdir(path):
    url = f'{hdfs_url}/webhdfs/v1{path}?user.name=hdfs&op=MKDIRS'
    
    try:
        response = requests.put(url)
        response.raise_for_status()
        data = response.json()
        
        print(data)
        print('MKDIR succesfully')
        
        return(True, None)

    except requests.exceptions.HTTPError as errh:
        return (False, f'HTTP Error: {errh}')
    except requests.exceptions.ConnectionError as errc:
        return (False, f'Error Connecting: {errc}')
    except requests.exceptions.Timeout as errt:
        return (False, f'Timeout Error: {errt}')
    except requests.exceptions.RequestException as err:
        return (False, f'Request Exception: {err}')
    
def rmdir(path):
    url = f'{hdfs_url}/webhdfs/v1{path}?user.name=hdfs&op=DELETE&recursive=true'
    
    try:
        response = requests.delete(url)
        response.raise_for_status()
        data = response.json()
        
        print(data)
        print('RMDIR succesfully')
        
        return(True, None)

    except requests.exceptions.HTTPError as errh:
        return (False, f'HTTP Error: {errh}')
    except requests.exceptions.ConnectionError as errc:
        return (False, f'Error Connecting: {errc}')
    except requests.exceptions.Timeout as errt:
        return (False, f'Timeout Error: {errt}')
    except requests.exceptions.RequestException as err:
        return (False, f'Request Exception: {err}')
    
# check connection
def check_connection():
    try:
        r = requests.get(hdfs_url)
        print("pb conn success")
        return True
    except Exception as e:
        print(str(e))
        print("pb conn failed")
        return False