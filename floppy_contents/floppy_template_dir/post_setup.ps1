. A:\config.ps1

Enable-PSRemoting -force
Set-Item WSMan:\localhost\Client\TrustedHosts * -force
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
restart-Service winrm

# Map test data drive from host
net use V: \\$smbserver\test /user:vmtest vmtest /persistent:yes

# Disable firewall to avoid weirdness
netsh advfirewall set allprofiles state off

# Allow unsigned PS scripts
Set-ExecutionPolicy -ExecutionPolicy Bypass -Force

# Set power scheme to "High performance"
powercfg /s scheme_min
# Disable timeout for display
powercfg -x monitor-timeout-ac 0

# Disable Windows Update
# http://support.microsoft.com/kb/328010
New-Item HKLM:\SOFTWARE\Policies\Microsoft\Windows -Name WindowsUpdate
New-Item HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate -Name AU
New-ItemProperty HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU -Name NoAutoUpdate -Value 1

# Reboot for hostname change in auto.ps1
shutdown -r -t 0
