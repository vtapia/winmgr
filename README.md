winmgr
============

This "project" was born to reduce the installation time of Windows VMs for testing, deploying via QEMU + libvirt, with an unattended installation.

Currently the IPs and other configs are hardcoded, but are easily changeable.

The contents of floppy_contents/floppy_template are used to create a floppy disk that will persist after reboots. This same floppy contains the answers file for unattended install (make sure to add the serial code of the windows release to install in config/os\_config.yml)

How to use it
-------------

These are the current parameters:

```
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
```

A typical call would be:

```
python ./cli.py deploy -n VM1 --disk format=raw,driver=ide,file=VM1.img,size=40 --net driver=e1000,mac=52:54:00:F2:50:A7,network=external,ip=192.168.220.17 --os user=utest,password=ptest,release=2012UI --vcpus=4 --ram=4 --balloon
```
