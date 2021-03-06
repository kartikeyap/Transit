#!/usr/bin/env python

import os
import socket
import platform

from logger import LOGGER
from datetime import datetime
from versions import OSX_VERSIONS
from subprocess import Popen, PIPE

from plist_dir.plist import Get_Plist_Info


class Gather_System_Info(object):

    def __init__(self):
        # Paths!
        self.root_agents = "/Library/LaunchAgents/"
        self.root_daemons = "/Library/LaunchDaemons/"
        # User launchAgents
        self.home_agents = "/Users/%s/Library/LaunchAgents"

    def shell_cmd(self, cmd):
        """
        Runs a shell command
        """
        # Logs all shell commands for safety.
        LOGGER.info('Starting shell_cmd method with the following command: %s' % cmd)
        # This method runs a shell command.
        return Popen(cmd.split(' '),
                     stdout=PIPE, stderr=PIPE).communicate()[0].strip('\n').split('\n')

    def return_platform_info(self):
        """
        Returns some info about the system processor
        """
        proc_info = platform.platform()
        if proc_info:
            return proc_info

    def return_hostname(self):
        """
        Returns hostname
        """
        hostname = socket.gethostname()
        if hostname:
            LOGGER.info('Returning hostname')
            return hostname

    def return_directory_contents(self, path):
        """
        This method will list a directories contents
        """
        # Change directory to the path in question
        dir_contents = []
        os.chdir(path)
        LOGGER.info('Changing directory to %s' % path)
        for i in os.listdir('.'):
            dir_contents.append(i)
        LOGGER.info('Returning directory contents for %s' % path)
        return dir_contents

    def return_home_dirs_with_paths(self):
        """
        Returns a list of home directories.
        """
        # This will gather a list of home directories.
        directories = []
        path = '/Users'
        os.chdir(path)
        home_dirs = os.listdir(path)
        for directory in home_dirs:
            if not directory.startswith('.'):
                directories.append('%s/%s' %(path, directory))
        LOGGER.info('Returning home directories with paths')
        return directories

    def return_home_dirs(self):
        """
        Returns a list of home directories.
        """
        # This will gather a list of home directories.
        directories = []
        path = '/Users'
        os.chdir(path)
        home_dirs = os.listdir(path)
        for directory in home_dirs:
            if not directory.startswith('.'):
                directories.append(directory)
        LOGGER.info('Returning home directories')
        return directories

    def return_list_of_users(self):
        """
        This will return a list of all users. (including system users)
        """
        user_list = []
        list_users = self.shell_cmd('dscacheutil -q user')
        if list_users:
            for user in list_users:
                if user.startswith('name: '):
                    user_list.append(user[6:])
        LOGGER.info('Returning users.')
        return user_list

    def return_open_with_internet(self):
        """
        Returns a list of open files using an internet connection.
        """
        lsof_i_list = []
        lsofi = self.shell_cmd('lsof -i')
        if lsofi:
            for files in lsofi:
                lsof_i_list.append(files)
        LOGGER.info('Returning list of open file')
        return lsof_i_list

    def return_open_files(self):
        """
        Returns a list of open files using an internet connection.
        """
        lsof_list = []
        lsofi = self.shell_cmd('lsof')
        if lsofi:
            for files in lsofi:
                lsof_list.append(files)
        LOGGER.info('Returning list of open file')
        return lsof_list

    def return_cron_tab(self, user):
        """
        Returns a list of crons associated to a user
        """
        cron_list = []
        crontab = self.shell_cmd('/usr/bin/crontab -u %s -l' % user)
        # yeeesh finally got this right.
        for i in crontab:
            if len(i) > 1:
                print "[+] User: %s Cron: %s" % (user, i)

    def return_os_build(self):
        """
        Shells out and returns the build of the operating system.
        """
        output = []
        os_build = self.shell_cmd('sw_vers -buildVersion')
        if os_build[0].isalnum():
            LOGGER.info('Returning OS Build')
            return os_build[0]

    def return_os_version(self):
        """
        Returns the operating system version.
        """
        os_version = platform.mac_ver()[0]
        LOGGER.info('Returning OS Version')
        return os_version

    def return_os_version_name(self):
        """
        Returns an os version name. Uses versions.py to verify os_name
        """
        os_names = []
        # Gathers a list of osx version keys
        for key in OSX_VERSIONS:
            os_names.append(key)
            # Takes those keys and loops over the dictionary
        for os_name in os_names:
            if self.return_os_version() in OSX_VERSIONS[os_name]:
                LOGGER.info('Returning OS Name')
                return os_name

    def return_process_list(self):
        """
        Returns a process list.
        """
        processes = []
        ps_list = self.shell_cmd('ps -A')
        for process in ps_list:
            processes.append(process)
        LOGGER.info('Returning processes')
        return processes

    def return_bash_history(self):
        """
        Returns a list of bash history
        """
        bash_history = []
        history = self.shell_cmd('history')
        try:
            if history:
                for line in history:
                    bash_history.append(line)
            LOGGER.info('Returning bash history')
            return bash_history
        except OSError:
            LOGGER.error('OSError')

    def return_all_bash_history(self, user):
        """
        This will return a specific user's (or users if looped) .bash_history in a list
        """
        # bash_history = []
        bash_history = {}
        with open('/Users/%s/.bash_history' % user, 'r') as all_history:
            if all_history:
                for line in all_history:
                    bash_history.append(line)
        LOGGER.info('Returning all bash history')
        return bash_history

    def list_directory_contents(self, path):
        """
        This will list the contents of a specific directory.
        """
        gpli = Get_Plist_Info()
        if os.path.exists(path):
            path_contents = os.listdir(path)
            for item in path_contents:
                if item.endswith('.plist'):
                    print gpli.main(item)

    def return_wireless_networks(self):
        """
        This will return the list of preferred wireless networks.
        """
        wifi_list = []
        # We are shelling out for this, and assuming wifi is on interface en0
        # for i in self.shell_cmd('/usr/sbin/networksetup -listpreferredwirelessnetworks en0'):
        #    wifi_list.append(i)
        # This will check that the wireless interface is valid
        # Using the bash output to match on.
        # if wifi_list[0].lower().startswith('preferred'):

        #        return wifi_list

        # If the interface is wrong, present the user with the location of the code
        # or maybe prompt them to add it. OR just bail completely well get there.
        # else:
        #    print "[!] Wireless interface is invalid, go to line 175 in helper.py to fix."
        output = self.shell_cmd('/usr/sbin/networksetup -listpreferredwirelessnetworks en0')        
        if 'error' in output[1].lower():
            output = self.shell_cmd('/usr/sbin/networksetup -listpreferredwirelessnetworks en1')
        
        for i in output:
            wifi_list.append(i)
        return wifi_list

    def tar_log_directory(self):
        """
        tars up the log directory
        """
        path_root = "/var/log"
        # TODO add local user logging directories too
        timestamp = datetime.today().strftime('%Y-%m-%d-%S')
        if os.path.exists(path_root):
            self.shell_cmd('tar czf log_%s.tar.gz %s' % (timestamp, path_root))
            return "[+] %s Zipping up %s directory. " % (timestamp, path_root)
    
    def show_last_reboot(self):
        """
        This will return a list of data regarding the last time 
        the machine was rebooted.
        """
        output = self.shell_cmd('last reboot')
        output_list = []
        if output:
            for i in output:
                output_list.append(i)
        return output_list

    def show_last_shutdown(self):
        """
        This method will return a list of information about when 
        the machine was last shutdown.
        """
        output = self.shell_cmd('last shutdown')
        output_list = []
        if output:
            for i in output:
                output_list.append(i)
        return output_list

    def return_diskspace(self):
        """
        Shells out and returns the disk space on all mounts.
        """
        output = self.shell_cmd('df -h') 
        output_list = []
        if output:
            for i in output:
                output_list.append(i)
        return output_list

    def return_system_uptime(self):
        """
        Shells out and returns the system uptime
        """
        output = self.shell_cmd('/usr/bin/uptime')
        output_list = []
        if output:
            for i in output:
                output_list.append(i)
        return output_list

    def return_logged_in_users(self):
        """
        Returns a list of logged in users.
        """
        output = self.shell_cmd('/usr/bin/w')
        output_list = []
        if output:
            for i in output:
                output_list.append(i)
        return output_list

    def return_any_screen_sessions(self):
        """
        Returns any active screen sessions
        """
        output = self.shell_cmd('/usr/bin/screen -ls')
        if output:
            return output

    def return_system_memory(self):
        """
        Returns a string containing how much memory is onboard.
        Kind of a hack, I am not super thrilled with this one.
        """
        output = self.shell_cmd('system_profiler SPHardwareDataType')
        if output:
            # hard coding the 12th item in the index to memory. Don't go changing!
            memory = output[12].strip()
            if memory.lower().startswith('memory'):
                return memory
            else:
                return "Error returning system memory"

    def return_uuid(self):
        """
        Returns a string containing how much memory is onboard.
        Kind of a hack, I am not super thrilled with this one.
        """
        output = self.shell_cmd('system_profiler SPHardwareDataType')
        if output:
            # hard coding the 12th item in the index to memory. Don't go changing!
            uuid = output[16].strip()
            if uuid.lower().startswith('hardware'):
                return uuid
            else:
                return "Error returning Hardware UUID"

    def return_macos_serial_number(self):
        """
        Same as above, it returns the serial number, but not in the best way.
        """
        output = self.shell_cmd('system_profiler SPHardwareDataType')
        if output:
            serial = output[15].strip()
            if serial.lower().startswith('serial'):
                return serial
            else:
                return "Error returning serial number"

    def return_processor_speed(self):
        """
        Returns processor speed
        """
        processor_list = []
        output = self.shell_cmd('system_profiler SPHardwareDataType')
        if output:
            speed = output[7].strip()
            cores = output[9].strip()
            proc_name = output[6]
            num_procs = output[8]
            if speed.lower().startswith('processor'):
                processor_list.append(speed)
                processor_list.append(cores)
                processor_list.append(proc_name)
                processor_list.append(num_procs)
            else:
                return "Error returning processor"
        return processor_list

    def return_other_very_random_info(self):
        """
        Literally as the method name is, there is some system info
        that is interesting but doesn't fit in a better section.
        """
        hardware_list = []
        output = self.shell_cmd('system_profiler SPHardwareDataType')
        if output:
            model_id = output[5].strip()
            model_name = output[4].strip()
            boot_rom = output[13].strip()
            smc_version = output[14].strip()
            return model_id, model_name, boot_rom, smc_version

