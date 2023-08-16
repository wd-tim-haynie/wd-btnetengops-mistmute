from mistlib import *
from tabulate import tabulate


def main():
    sites = get_sites()

    mod_mute = True

    while mod_mute:
        get_mutes(sites)

        resp = ''
        while resp != 'y' and resp != 'n':
            resp = input("\nWould you like to make changes to mutes? 'y' or 'n': ").lower()
            if resp == 'y':
                mod_mute = True
            elif resp == 'n':
                mod_mute = False
            else:
                print("Please respond with 'y' or 'n'.")

        if mod_mute:
            siteid = Select_Site(sites)
            seconds = Seconds()
            start_time_epoch = None
            if seconds > 0:
                start_time_epoch = start_time()
            Mute(siteid, start_time_epoch, seconds)

    sesh.close()


def get_mutes(sites):
    url = f"{murl}/orgs/{orgid}/alarmtemplates/suppress"

    req = sesh.get(url, headers=my_headers)

    if req.json()['results'] == []:
        print("\nNo active mutes!")

    else:

        mute_data = []

        for mute in req.json()['results']:

            for site in sites:
                if mute['site_id'] == site['id']:
                    name = site['name']
                    break

            #duration_str = ConvertSeconds(mute['duration'])
            start_time_str = epoch_to_human((mute['scheduled_time']))

            if mute['scheduled_time'] < datetime.now().timestamp():
                end_time_epoch = datetime.now().timestamp() + mute['duration']
                end_time_str = epoch_to_human(end_time_epoch)
                mute_data.append([name, start_time_str, end_time_str, "Muted Now"])
            else:
                end_time_epoch = mute['scheduled_time'] + mute['duration']
                end_time_str = epoch_to_human(end_time_epoch)
                mute_data.append([name, start_time_str, end_time_str, "Scheduled"])

        # end of outer loop

        sorted_mute_data = sorted(mute_data, key=lambda x: x[0])
        header_row = ['Site', 'Start Time', 'End Time', 'Mute Status']
        mute_table = tabulate(sorted_mute_data, headers=header_row, tablefmt='orgtbl')

        print("\nActive Mutes:")
        print(mute_table)


main()