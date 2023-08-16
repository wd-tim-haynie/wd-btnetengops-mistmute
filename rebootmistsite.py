from mistlib import Mute, get_sites, Select_Site
import requests
from os import getenv
from time import sleep

murl = 'https://api.mist.com/api/v1'
my_headers = {"Authorization": f"Token {getenv('MIST_TOKEN')}",
              "Content-Type": "application/json"}
sesh = requests.Session()
orgid = sesh.get(f"{murl}/self", headers=my_headers).json()['privileges'][0]['org_id']  # assumes only 1 item returned

def reboot():
    print("reboot a site 1 AP at a time")
    siteid = Select_Site(get_sites())

    url = f"{murl}/sites/{siteid}/devices"
    devices = sesh.get(url, headers=my_headers).json()

    # mute the site
    Mute(siteid, None, seconds=len(devices)*60+120)

    #reboot the devices
    for device in devices:
        if device["type"] == "ap":
            url = f"{murl}/sites/{siteid}/devices/{device['id']}/restart"
            req = sesh.post(url, headers=my_headers)
            if req.status_code == 200:
                print(f"rebooted {device['name']}")
                sleep(60)
            else:
                print(f"error {device['name']}")



reboot()
