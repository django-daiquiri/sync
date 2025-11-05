import configparser
import subprocess
import yaml


class Ansible():

    def __init__(self, inventory_file, playbook_file, extra_nodes_indexes = []):
        self.inventory_file = inventory_file
        self.playbook_file = playbook_file
        self.extra_nodes_indexes = extra_nodes_indexes
        self.extra_nodes = []

        # parse the ansible inventory file
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read(inventory_file)

        # set the list of host_groups
        self.host_groups = config.sections()

        # set the dict of hosts, seperated by host_group
        self.hosts = {}
        for host_group in self.host_groups:
            self.hosts[host_group] = [name for name, _ in config.items(host_group)]

        # get the head node
        self.head_node = self.hosts[self.host_groups[0]][0]
        for extra_node_index in self.extra_nodes_indexes:
            self.extra_nodes.append(self.hosts[self.host_groups[extra_node_index]][0])

        # initialize the plays dict, seperated by host_group
        self.plays = {}
        for host_group in self.host_groups:
            self.plays[host_group] = {
                'name': 'Sync %s' % host_group,
                'hosts': host_group,
                'remote_user': 'root',
                'tasks': []
            }

        # add a play for the head node
        self.plays[self.head_node] = {
            'name': 'Sync %s' % self.head_node,
            'hosts': self.head_node,
            'remote_user': 'root',
            'tasks': []
        }
        # add a play for the extra nodes
        for extra_node in self.extra_nodes:
            self.plays[extra_node] = {
                'name': 'Sync %s' % extra_node,
                'hosts': extra_node,
                'remote_user': 'root',
                'tasks': []
            }


    def play(self, dry=False):
        # convert the plays dict to a yaml, but preserving the order of host_groups
        plays = [self.plays[hosts] for hosts in self.host_groups + [self.head_node] + self.extra_nodes]
        playbook_yaml = yaml.dump(plays)

        # write the yaml into a (secure) temporary file
        with open(self.playbook_file, 'w') as f:
            f.write(playbook_yaml)

        # call ansible using a subprocess
        args = ['ansible-playbook', '--inventory=%s' % self.inventory_file, self.playbook_file]

        if dry:
            subprocess.call(args + ['--check'])
        else:
            subprocess.call(args)
