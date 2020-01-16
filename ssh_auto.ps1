$Password = "raspberry"
$User = "pi"
$ComputerName = "192.168.0.27"
$Command = "cd /home/pi && touch ballbags "

$secpasswd = ConvertTo-SecureString $Password -AsPlainText -Force
$Credentials = New-Object System.Management.Automation.PSCredential($User, $secpasswd)

$SessionID = New-SSHSession -ComputerName $ComputerName -Credential $Credentials #Connect Over SSH

Invoke-SSHCommand -Index $sessionid.sessionid -Command $Command # Invoke Command Over SSH