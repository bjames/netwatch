from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException, logging
from time import sleep
from datetime import datetime
from sys import argv
from functools import partial
from multiprocessing import Pool
from yaml import safe_load

import getpass


def print_output(device_result):

    for i in range(len(device_result['results'])):

        print('\n!!!!!!! {} on {} at {}\n\n{}'.format(device_result['commands'][i],
                                                device_result['hostname'],
                                                device_result['timestamps'][i],
                                                device_result['results'][i]))


def write_output(device_result):

    with open('netwatch_output_{}.log'.format(device_result['hostname']), 'a') as outfile:

        for i in range(len(device_result['results'])):

            outfile.write('\n!!!!!!! {} on {} at {}\n\n{}'.format(device_result['commands'][i],
                                                    device_result['hostname'],
                                                    device_result['timestamps'][i],
                                                    device_result['results'][i]))


def execute_commands(device_settings, username, password):

    """
        Runs commands on a device and returns a dictionary object with the device name and the results
    """

    output = []
    timestamps = []

    try:

        ssh_session = ssh_connect(device_settings['hostname'], device_settings['device_type'],
                                device_settings['port'], username, password)

    # write any exceptions to output so they are recorded in the results
    except Exception as e:

        output = ['Exception occured before SSH connection: {}'.format(e)] * len(device_settings['commands'])
        timestamps = [datetime.now()] * len(device_settings['commands'])

    # only executes if no exceptions occur
    else:

        for command in device_settings['commands']:

            try:

                output.append(ssh_session.send_command(command))

            except IOError:

                output.append('COMMAND TIMED OUT')

            except Exception as e:

                output.append('Exception after SSH connection: {}'.format(e))
            
            finally:

                timestamps.append(datetime.now())

    device_result = {
        'hostname': device_settings['hostname'],
        'commands': device_settings['commands'],
        'results': output,
        'timestamps': timestamps
    }

    return device_result


def ssh_connect(hostname, device_type, port, username, password):

    """
        connects to a device and returns a netmiko ssh object
    """

    device = {
        'device_type': device_type,
        'ip': hostname,
        'username': username,
        'password': password,
        'port': port
    }

    return ConnectHandler(**device)


def get_validate_credentials(hostname, device_type, port):

    """
        gets username and password, opens an ssh session to verify the credentials
        then closes the ssh session
        
        returns username and password

        Doing this prevents multiple threads from locking out an account due to mistyped creds
    """

    # attempts to get the username, prompts if needed
    username = input('Username: ')

    # prompts user for password
    password = getpass.getpass()

    authenticated = False

    while not authenticated:

        try:

            test_ssh_session = ssh_connect(hostname, device_type, port, username, password)
            test_ssh_session.disconnect()

        except NetMikoAuthenticationException:

            print('authentication failed on ' + hostname + ' (CTRL + C to quit)')

            username = input('Username: ')
            password = getpass.getpass()

        except NetMikoTimeoutException:

            print('SSH timed out on ' + hostname)
            raise

        else:

            # if there is no exception set authenticated to true
            authenticated = True

    return username, password


def merge_settings(device, script_config):

    ''' merges the default and device specific dictionaries '''

    device_settings = script_config['default'].copy()
    device_settings.update(device)

    return device_settings


def set_device_settings(script_config):

    '''
        creates an array of devices containing device specific
        script configuration
    '''

    device_settings = []

    for device in script_config['device_list']:

        device_setting = merge_settings(device, script_config)
        device_settings.append(device_setting)

    return device_settings


def main():

    try:

        config_file_name = argv[1]

    except IndexError:

        config_file_name = 'netwatch.yml'

    # pull data from config file
    script_config = safe_load(open(config_file_name))

    # create the device settings list
    device_settings = set_device_settings(script_config)

    # get valid credentials from the user
    username, password = get_validate_credentials(device_settings[0]['hostname'], device_settings[0]['device_type'], device_settings[0]['port'])
    
    iter = 0
    while script_config['max_iter'] == 0 or script_config['max_iter'] > iter:

        print('running commands')

        # execute on each device in the device list in parallel 
        with Pool(script_config['threads']) as pool:

            # create a partial function, then use pool.map passing in the device_settings list
            device_results = pool.map(partial(execute_commands,
                                            username=username,
                                            password=password),
                                device_settings)

        iter += 1

        # Iterate over our device_results and write it to a file/print to screen
        for device_result in device_results:

            if script_config['file_output']:

                try:

                    write_output(device_result)

                except Exception as e:

                    print('Exception occured while writing to file for {}'.format(device_result['hostname']))
                    print(e)

            if script_config['print_output']:

                    print_output(device_result)

        print('loop has excuted {} time(s), last execution completed at {}'.format(iter, datetime.now()))
        print('maxium iterations is {} (when set to 0 loop executes forever)'.format(script_config['max_iter']))

        if script_config['max_iter'] > iter:

            print('sleeping for {} seconds (CTRL+C to quit)'.format(script_config['sleep_time']))
            sleep(script_config['sleep_time'])

main()