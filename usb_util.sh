#!/bin/bash
set -x

ACTION=$1
DOM=$2
CPDIR=$3
USBFILE=${4:-/tmp/usbdisk.img}

verify_add() {
virsh dominfo $DOM >/dev/null 2>&1
if [[ $? != 0 ]]
then
	echo "Domain $DOM does not exist"
	exit 1
fi

if [ ! -s $CPDIR ]
then
	echo "Path to file $CPDIR does not exist"
	exit 1
fi
}

verify_del() {
virsh dominfo $DOM >/dev/null 2>&1
if [[ $? != 0 ]]
then
	echo "Domain $DOM does not exist"
	exit 1
fi
}

add() {
sudo virsh qemu-monitor-command --hmp $DOM "drive_add 0 if=none,format=raw,id=usbdisk1,file=$CPDIR"
sudo virsh qemu-monitor-command --hmp $DOM "device_add usb-storage,id=usbdisk1,drive=usbdisk1"
}

create_disk() {
	MNT_DIR=$(mktemp -d)

	echo "Generating new floppy image: $USBFILE"
	# qemu-img create -f raw -o size=1G -o preallocation=falloc $USBFILE
	qemu-img create -f raw -o size=100M $USBFILE

	# mkfs.ntfs -F $USBFILE
	mkfs.vfat $USBFILE
	sudo mount -o loop -t vfat -o rw,uid=$UID $USBFILE $MNT_DIR
	cp -R ${CPDIR}/* ${MNT_DIR}
	tree $MNT_DIR
	TOTAL_SIZE=`du -sh $MNT_DIR`
	echo "Total size: $TOTAL_SIZE"
	sync
	sudo umount $MNT_DIR
	sudo rmdir $MNT_DIR
	chmod 777 $USBFILE

	echo "USB disk $USBFILE created."
}

delete_disk() {
	rm /tmp/usbdisk.img
}

del() {
virsh qemu-monitor-command --hmp $DOM "device_del usbdisk1"
}

case $ACTION in
	add )
		if [[ $# -ne 3 ]]; then
			echo "Wrong number of parameters"
			echo "Usage: $0 add <virsh domain> <file to attach>"
			exit 1
		fi
		verify_add
		add
		;;
	create )
		if [[ $# -ne 4 ]]; then
			echo "Wrong number of parameters"
			echo "Usage: $0 create <virsh domain> <dir to copy> <usb disk image file>"
			exit 1
		fi
		create_disk
		;;
	del )
		if [[ $# -ne 2 ]]; then
			echo "Wrong number of parameters"
			echo "Usage: $0 del <virsh domain>"
			exit 1
		fi
		del
		delete_disk
		;;
	* )
		echo "$ACTION is not add/del"
		exit 1
		;;
esac
