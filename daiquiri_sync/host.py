import csv
import io

import paramiko


class Host():

    def __init__(self, name='localhost', user='root', uid_range=[10000, 20000]):
        self.name = name
        self.user = user
        self.uid_range = uid_range

        # init the paramiko ssh connection
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(name, username=user, allow_agent=True)

        # get the list of users and groups from the host
        self.users = self.get_users()
        self.groups = self.get_groups()

        # create maps for users and groups
        self.user_map = {user['name']: user for user in self.users}
        self.group_map = {group['name']: group for group in self.groups}

        # init the uid creation
        self.current_uid, self.max_uid = self.uid_range
        self.uid_list = [u['uid'] for u in self.users]

    def create_uid(self):
        while self.current_uid < self.max_uid - 1:
            self.current_uid += 1
            if self.current_uid not in self.uid_list:
                return self.current_uid

        raise Exception('No uid remaining in uid_range')

    def get_users(self):
        stdin, stdout, stderr = self.client.exec_command('cat /etc/passwd')

        passwd = []
        for row in csv.reader(stdout.read().decode().split('\n'), delimiter=':', quoting=csv.QUOTE_NONE):
            if row and len(row) >= 7:
                passwd.append({
                    'name': row[0],
                    'uid': int(row[2]),
                    'gid': int(row[3]),
                    'comment': row[4],
                    'home': row[5],
                    'shell': row[6]
                })

        return passwd

    def get_groups(self):
        stdin, stdout, stderr = self.client.exec_command('cat /etc/group')

        groups = []
        for row in csv.reader(stdout.read().decode().split('\n'), delimiter=':', quoting=csv.QUOTE_NONE):
            if row and len(row) >= 4:
                groups.append({
                    'name': row[0],
                    'gid': int(row[2]),
                    'users': row[3].split(',') if row[3] else []
                })

        return groups
