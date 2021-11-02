# Week 12: Setting up Win10 server

## Change default shell to PowerShell

    New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force

## Install OpenSSH

### Config SSH Server
[Config SSH Server](https://blog.devgenius.io/set-up-your-ssh-server-in-windows-10-native-way-1aab9021c3a6)

    Restart-Service -Name sshd, ssh-agent -Force

## Wake on LAN
### Server side (Win10)
[Enable and use Wake on LAN on Windows 10](https://www.windowscentral.com/how-enable-and-use-wake-lan-wol-windows-10)

### Client side (Linux)
[Wake up computer with Linux Command](https://www.cyberciti.biz/tips/linux-send-wake-on-lan-wol-magic-packets.html)

    sudo apt-get install etherwake
    wakeonlan 3c:84:6a:0c:f5:39

### Add wakeonlan command to VNC

Add the command "wakeonlan 3c:84:6a:0c:f5:39" as a pre-command to your VNC client to wake up the server every time you want to use the GUI.
