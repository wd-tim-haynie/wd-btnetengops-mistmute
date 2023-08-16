import requests
from os import getenv
from datetime import datetime
import time

murl = 'https://api.mist.com/api/v1'
my_headers = {"Authorization": f"Token {getenv('MIST_TOKEN')}",
              "Content-Type": "application/json"}
sesh = requests.Session()
orgid = sesh.get(f"{murl}/self", headers=my_headers).json()['privileges'][0]['org_id']  # assumes only 1 item returned


def epoch_to_human(epoch):

    # Convert epoch time to datetime object
    datetime_obj = datetime.fromtimestamp(epoch)

    # Convert datetime object to human-readable format displayed in system's timezone
    human_readable_time = datetime_obj.strftime("%Y-%m-%d %H:%M:%S ")

    return(human_readable_time + datetime.now().astimezone().tzname())  # Example output: 2021-03-30 12:00:00


def mist_get(uri):
    """Sends a GET to the specified URL, returns json"""
    return sesh.get(f"{murl}{uri}", headers=my_headers).json()


def mist_post(url, params):
    """Sends a POST to the specified URL with the specified parameters, returns the response"""
    return sesh.post(url, headers=my_headers, json=params)


def get_sites():
    url = f"{murl}/orgs/{orgid}/sites"

    sites_list = sesh.get(url, headers=my_headers).json()
    sites_list.sort(key=Name_Sort)

    return sites_list




def start_time():
    bad_input = True
    resp = ''

    while bad_input:
        resp = input("\nWould you like to mute immediately? (y/n) ")
        if resp == 'y' or resp == 'n':
            bad_input = False
        else:
            print("Please only respond with 'y' or 'n'.")

    if resp == 'y':
        return

    bad_input = True
    epoch = 0
    tz_offset = -int((time.timezone if (time.localtime().tm_isdst == 0) else time.altzone))
    tz_name = datetime.now().astimezone().tzname()

    while bad_input:

        print("\nValid start timestamps are between now and 1 week in the future.")
        print("Scheduled start time will be calculated based on your current timezone:", tz_name, tz_offset / 3600.0)

        date_str = input("Use the format 'YYYY/MM/DD HH:MM' (example: 2023/03/21 17:30): ")
        input_format = '%Y/%m/%d %H:%M'

        try:

            # convert the string to a datetime object named dt
            dt = datetime.strptime(date_str, input_format)
            # convert the datetime object to epoch time
            epoch = int(time.mktime(dt.timetuple()))

        except ValueError:
            print("ERROR: Invalid date/time entry, please try again.")
            continue
        except UnboundLocalError:
            print("ERROR: Invalid date/time entry, please try again. Make sure to include full date and time.")
            continue

        now = datetime.now().timestamp()

        # DEBUG
        # print(f"Now:    {now}")
        # print(f"epoch:  {epoch}")
        # print(f"1 week: {datetime.now().timestamp() + 604800.0}")  # 604800 seconds is 1 week

        if epoch < now:
            print("ERROR: Can't be a time in the past.")
            continue
        elif epoch > now + 604800:  # 604800 seconds = 1 week
            print("ERROR: Too far in the future.")
            continue
        else:
            bad_input = False

    # end of while bad_input loop

    return epoch


def Mute(siteid, start_time_ecoch, seconds):

    url = f"{murl}/orgs/{orgid}/alarmtemplates/suppress"

    my_params = {
        "duration": seconds,

        "applies": {
            "site_ids": [siteid]
        }
    }

    if start_time_ecoch is not None:
        my_params["scheduled_time"] = start_time_ecoch

    sesh.post(url, headers=my_headers, json=my_params)


def Seconds():

    error = True
    seconds = 0

    while error:

        print("\nMaximum mute time is 24 hours.")
        hours = int_catch("Mute for how many hours? (0 to unmute) ")
        seconds = (hours * 3600)

        if hours > 24 or hours < 0:
            print("ERROR: Invalid number of hours.")
            continue
        elif hours == 0:
            print(f"Site will be unmuted.")
            error = False
        else:
            print(f"Muting for {hours} hours.")
            error = False

    return seconds


def Name_Sort(dictionary):
    return dictionary['name']


def int_catch(promptstr):

    bad_input = True
    resp = ''
    while bad_input:
        try:
            resp = int(input(promptstr))
            bad_input = False
        except ValueError:
            print("Bad input, try again.")

    return resp


def Select_Site(sites):

    for index, site in enumerate(sites):
        print(f"{index}: {site['name']}")

    bad_input = True
    while bad_input:
        try:
            selection = int_catch("\nWhich site? ")
            siteid = sites[selection]['id']
            bad_input = False
        except IndexError:
            print("Bad input, try again.")

    print(f"Selected {sites[selection]['name']}")

    return siteid


def ConvertSeconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 3600) % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def yn(promptstr):
    selection = ''
    bad_input = True
    while bad_input:
        selection = input(promptstr).lower()
        if selection != 'y' and selection != 'n':
            print("Bad input, please respond with 'y' or 'n'.")
        else:
            bad_input = False
    return selection

def int_catch_max(promptstr, max_value):
    while True:
        user_input = int_catch(promptstr)
        if 0 <= user_input <= max_value:
            return user_input
        else:
            print(f"Please enter a number between 0 and {max_value}.")
