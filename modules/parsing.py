# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
import yaml


cfg_path = os.getcwd() + '/config/'
cfg_file = cfg_path + 'winmgrd.conf'


def parse_basic_resources(data):
    config = {}
    config['name'] = data.name
    if data.vcpus and data.ram:
        config['vcpus'] = data.vcpus
        config['ram'] = data.ram
    else:
        print("Missing vcpus or ram")
        exit(1)
    return config


def parse_disk_resources(data):
    with open(cfg_file, 'r') as f:
        cfg = yaml.load(f)

    config = {}
    config['disks'] = {}
    index = 1
    for disk in data:
        config['disks']['disk'+str(index)] = {}
        for info in data[index - 1].split(","):
            args = info.split("=")
            if args[0] == 'driver':
                if args[1] == 'ide' or args[1] == 'virtio':
                    config['disks']['disk'+str(index)][args[0]] = args[1]
                else:
                    print('Driver must be ide/virtio')
                    exit(1)
            elif args[0] == 'file':
                if isinstance(args[1], str) and args[1][-4:] == '.img':
                    config['disks']['disk'+str(index)][args[0]] = cfg['vm_path'] + args[1]
                else:
                    print('File must end in .img')
                    exit(1)
            elif args[0] == 'format':
                if args[1] == 'qcow2' or args[1] == 'raw':
                    config['disks']['disk'+str(index)][args[0]] = args[1]
                else:
                    print('Format must be qcow2/raw')
                    exit(1)
            elif args[0] == 'size':
                if re.match(r"(^[0-9]+)$", args[1]):
                    config['disks']['disk'+str(index)][args[0]] = args[1]
                else:
                    print('Size must be an integer')
                    exit(1)
        if config['disks']['disk'+str(index)]:
            index += 1
    if config['disks']['disk1']:
        return config
    else:
        return None


def parse_os_resources(data):
    config = {}
    config['os'] = {}
    for info in data[0].split(","):
        args = info.split("=")
        if args[0] == 'release':
            if re.match(r"(^2012)(R2)?(UI)?|(2016)(UI)?$", args[1]):
                # check 2012, 2012R2, 2016
                config['os'][args[0]] = args[1]
            else:
                print('Release has to be 2012, 2012R2 or 2016')
                exit(1)
        elif args[0] == 'user':
            config['os'][args[0]] = args[1]
        elif args[0] == 'password':
            config['os'][args[0]] = args[1]
    if config['os']:
        return config
    else:
        return None


def parse_net_resources(data):
    config = {}
    config['nics'] = {}
    index = 1
    for disk in data:
        config['nics']['nic'+str(index)] = {}
        for info in data[index - 1].split(","):
            args = info.split("=")
            if args[0] == 'driver':
                if args[1] == 'e1000' or args[1] == 'virtio':
                    config['nics']['nic'+str(index)][args[0]] = args[1]
                else:
                    print('Driver must be e1000/virtio')
                    exit(1)
            elif args[0] == 'network':
                if args[1] == 'internal' or args[1] == 'external':
                    config['nics']['nic'+str(index)][args[0]] = args[1]
                else:
                    print('Network must be internal or external')
                    exit(1)
            elif args[0] == 'ip':
                if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", args[1]):
                    config['nics']['nic'+str(index)][args[0]] = args[1]
                else:
                    print('IP format should be 111.2.33.444')
                    exit(1)
            elif args[0] == 'mac':
                if re.match(r"^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$", args[1]):
                    config['nics']['nic'+str(index)][args[0]] = args[1]
                else:
                    print('MAC format should be AA:BB:CC:DD:EE:FF')
                    exit(1)
        if config['nics']['nic'+str(index)]:
            index += 1
    if config['nics']['nic1']:
        return config
    else:
        return None


def parse_virtio_resources(data):
    config = {}
    if data.balloon:
        config['balloon'] = True
    if data.serial:
        config['serial'] = True
    if data.entropy:
        config['entropy'] = True
    if config:
        return config
    else:
        return None
