import os
import sys
import json
import requests

DEBUG = True
API_NAMESPACE=409723

def getBaseUrl(instance):
    baseUrl = "%s/api" %(instance);
    if DEBUG:
        print("baseUrl: " + baseUrl)
    return baseUrl

def processChangeRequestResponse(function, response):
    status = 'OK'
    env_file_path = "/meta/env_vars_to_export"

    print("Processing answer from REST call")
    if (response.status_code != 200 and response.status_code != 201):
        print("Change Request creation failed with code %s" % (response.status_code))
        print("Error: " + response.text)
        status= 'ERROR'
        return response.status_code

    print("Change Request creation successful")
    data=json.loads(response.text)
    CR_NUMBER=data["result"]["number"]
    CR_SYSID=data["result"]["sys_id"]
    FULL_JSON=json.dumps(data, indent=2)
    print(f"Change Request Number: {CR_NUMBER}")
    print(f"Change Request sys_id: {CR_SYSID}")
    print("Change Request full answer:\n" + FULL_JSON)

    if os.path.exists(env_file_path):
        env_file = open(env_file_path, "a")
        env_file.write(f"CR_NUMBER={CR_NUMBER}\n")
        env_file.write(f"CR_SYS_ID={CR_SYSID}\n")
        env_file.write("CR_FULL_JSON=/codefresh/volume/servicenow-cr.json\n")
        env_file.close()

        json_file=open("/codefresh/volume/servicenow-cr.json", "w")
        json_file.write(FULL_JSON)
        json_file.close()

def createChangeRequest(user, password, baseUrl, title, data, description):

    if DEBUG:
        print("Entering createChangeRequest:")
        print("Body: " + data)

    if (bool(data)):
        crBody=json.loads(data)
    else:
        crBody= {}

    crBody["cf_build_id"] = os.getenv('CF_BUILD_ID')


    url="%s/now/table/change_request" % (baseUrl)

    if DEBUG:
        print(f"Entering createChangeRequest:")
        print(f"URL: {url}")
        print(f"User: {user}")
        print(f"Body: {crBody}")

    resp=requests.post(url,
        json = crBody,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processChangeRequestResponse(function="createChangeRequest", response=resp)

def main():
    global DEBUG

    ACTION = os.getenv('action', 'createCR').lower()
    USER = os.getenv('SN_USER')
    PASSWORD = os.getenv('SN_PASSWORD')
    INSTANCE = os.getenv('SN_INSTANCE')
    DATA     = os.getenv('data')

    #DEBUG = True if os.getenv('debug', "false").lower == "true" else False
    TITLE = os.getenv('title', 'Change Request created by Codefresh')
    DESCRIPTION = os.getenv('description', '')

    if ACTION == "createcr":
        createChangeRequest(user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            title=TITLE,
            data=DATA,
            description=DESCRIPTION)
if __name__ == "__main__":
    main()
