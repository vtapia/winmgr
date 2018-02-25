# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import libvirt
import logging
import jinja2
import yaml

cfg_path = os.getcwd() + '/config/'
cfg_file = cfg_path + 'winmgrd.conf'

with open(cfg_file, 'r') as f:
        cfg = yaml.load(f)

base_path = os.getcwd()

tmpl_path = cfg_path + 'templates/'
floppy_path = base_path + '/floppy_contents/'
floppy_base = floppy_path + 'floppy_template_dir/'

templateLoader = jinja2.FileSystemLoader(searchpath=tmpl_path)
templateEnv = jinja2.Environment(loader=templateLoader)

networks = ['internal', 'external']

logger = logging.getLogger('Deploy')

logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fmt = logging.Formatter('%(asctime)s %(levelname)s: [Deploy] %(message)s', datefmt='%d/%m/%Y %T')
ch.setFormatter(fmt)
logger.addHandler(ch)


def deploy_guest(guest):

    lv = libvirt.open('qemu:///system')

    logger.info("- Setting up networks")
    net_setup(lv)
    disk_setup(guest)
    floppy_setup(guest)
    domxml = guest_template_setup(lv, guest, cfg)
    define_vm(lv, domxml, guest)
    # start VM


def net_setup(lv):

    for network in networks:

        net_tmpl = tmpl_path + 'net_' + network + '.xml'

        with open(net_tmpl, 'r') as f:
            net_xml = f.read()

        try:
            vnet = lv.networkLookupByName(network)
            if vnet.isActive():
                pass
        except libvirt.libvirtError:
            logger.info("Network " + network + " does not exist: Creating")
        finally:
            try:
                vnet = lv.networkDefineXML(net_xml)
                vnet.setAutostart(True)
                vnet.create()
            except libvirt.libvirtError:
                logger.error("Failed creating network " + network + "!")


def disk_setup(guest):
    for disk in guest['disks']:
        diskfile = guest['disks'][disk]['file']
        if not os.path.exists(diskfile):
            os.system('rm ' + diskfile)
            os.system('qemu-img create -f ' + guest['disks'][disk]['format'] + ' ' +
                      diskfile + ' ' + guest['disks'][disk]['size'] + 'G')
        else:
            print("File %s already exists" % diskfile)


def os_setup(guest):
    template = templateEnv.get_template('Autounattend_template.xml')
    with open(cfg_path + "os_config.yml", 'r') as f:
        os_list = yaml.load(f)

    release = guest['os']['release']
    size = guest['disks']['disk1']['size'] + '000'
    autounattend = template.render(os_list['OS'][release], user=guest['os']['user'],
                                   password=guest['os']['password'], size=size)
    return autounattend


def floppy_setup(guest):

    if not os.path.exists(floppy_path + guest['name']):
        os.makedirs(floppy_path + guest['name'])

    # Populate usb directory
    os.system("cp -r " + floppy_base + "* " + floppy_path + guest['name'])

    # Prepare autounattend
    autounattend = os_setup(guest)
    with open(floppy_path + guest['name'] + "/Autounattend.xml", "w") as f:
        f.write(autounattend)

    # Create .img disk
    floppy_disk_setup(guest)


def floppy_disk_setup(guest):

    os.system(base_path + "/usb_util.sh create " + guest['name'] + " " + floppy_path + guest['name'] +
              " " + cfg['vm_path'] + guest['name'] + '_floppy.img')


def guest_template_setup(lv, guest, cfg):

    template = templateEnv.get_template('guest_template.xml')

    with open(cfg_path + "os_config.yml", 'r') as f:
        os_config = yaml.load(f)

    os_version = guest['os']['release']
    cdrom_path = cfg['iso_path'] + os_config['OS'][os_version]['iso']
    floppy_path = cfg['vm_path'] + guest['name'] + '_floppy.img'

    vm_xml = template.render(guest, cdrom=cdrom_path, floppy=floppy_path)
    # print(vm_xml)
    return(vm_xml)


def define_vm(lv, vm_xml, guest):
    try:
        vm = lv.lookupByName(guest['name'])
        if vm.isActive():
            logger.info("VM " + guest['name'] + " exists: Destroying and recreating")
            vm.destroy()
        vm.undefine()
    except libvirt.libvirtError:
        logger.info("VM " + guest['name'] + " doesn't exist yet...")

    try:
        vm = lv.defineXML(vm_xml)
        vm.create()
        print("VM " + guest['name'] + " has been created.")
    except libvirt.libvirtError:
        logger.error("Failed creating VM " + guest['name'] + "!")
