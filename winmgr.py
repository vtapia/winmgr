# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import modules.parsing as parsing
import modules.deploy as deploy


def verify_mins(config):
    """
    Mins: disk/nic(all fields if present), os(all fields)
    ram and vcpus are already checked at this point
    """
    for disk in config['disks']:
        if not set(("file", "size", "driver", "format")) <= set(config['disks'][disk]):
            print(disk + " is missing information")
            exit(1)

    if 'nics' in config:
        for nic in config['nics']:
            if not set(("ip", "mac", "driver", "network")) <= set(config['nics'][nic]):
                print(nic + " is missing information")
                exit(1)

    if not set(("release", "user", "password")) <= set(config['os']):
            print("OS is missing information")
            exit(1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=['deploy', 'run'],
                        help="deploy/run")
    parser.add_argument("-n", "--name", type=str,
                        help="Guest name")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("--balloon", action="store_true",
                        help="Enable VirtIO balloon device")
    parser.add_argument("--entropy", action="store_true",
                        help="Enable VirtIO entropy device")
    parser.add_argument("--serial", action="store_true",
                        help="Enable VirtIO serial device")
    parser.add_argument("--vcpus", type=int,
                        help="Number of VCPUs")
    parser.add_argument("--ram", type=int,
                        help="RAM size in GB")
    parser.add_argument("--disk", type=str, action='append',
                        help="Define disk (e.g --disk driver=virtio,file=/tmp/disk.img,format=qcow2,size=40)")
    parser.add_argument("--net", type=str, action='append',
                        help="Define network interface (e.g --net ip=1.2.3.4,mac=a:b:c:d:e:f,driver=virtio,network=default)")
    parser.add_argument("--os", type=str, action='append',
                        help="Define OS config (e.g --os release=2016,autostart=script.ps1,usb_dir=path,user=vmtest,password=vmtest)")

    args = parser.parse_args()

    if args.action == "deploy":
        # minimum resources:
        # check vcpus/ram are defined
        config = parsing.parse_basic_resources(args)
        if not config:
            print('Basic resources (vcpus, ram) are required to deploy')
            exit(1)
        # check disk exists and includes file, driver, format and size
        ret = parsing.parse_disk_resources(args.disk)
        if ret:
            config.update(ret)
        else:
            print('At least one disk is required to deploy')
            exit(1)
        # check os
        ret = parsing.parse_os_resources(args.os)
        if ret:
            config.update(ret)
        else:
            print('OS configuration is required to deploy')
            exit(1)
        # optional:
        ret = parsing.parse_net_resources(args.net)
        if ret:
            config.update(ret)
        # virtio devices
        ret = parsing.parse_virtio_resources(args)
        if ret:
            config.update(ret)

        print('DEBUG: ' + str(config))

        verify_mins(config)
        deploy.deploy_guest(config)
