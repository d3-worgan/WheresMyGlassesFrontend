# Pi details
$Password = "raspberry"
$User = "pi"
$ComputerName = "192.168.0.27"

# SSH connection
$secpasswd = ConvertTo-SecureString $Password -AsPlainText -Force
$Credentials = New-Object System.Management.Automation.PSCredential($User, $secpasswd)
$SessionID = New-SSHSession -ComputerName $ComputerName -Credential $Credentials #Connect Over SSH

# Push changes to github
Write-Host "[out] Pushing action code to github..."
git add . 
git commit -m "debug" 
git push

# Login to pi and delete the old skills
Write-Host "[out] Deleting old skill from Pi..."
$Command = "sudo rm -r /var/lib/snips/skills/WheresMyGlassesFrontend/"
Invoke-SSHCommand -Index $sessionid.sessionid -Command $Command # Invoke Command Over SSH

# Download the new action code with Sam
Write-Host "[out] Downloading new actions to pi..."
sam install actions

# Login to pi and change permissions
Write-Host "[out] Setting new action code permissions..."
$Command = "sudo chmod +x /var/lib/snips/skills/WheresMyGlassesFrontend/action-FrontendManager.py"
Invoke-SSHCommand -Index $sessionid.sessionid -Command $Command # Invoke Command Over SSH

# Reinstall actions
Write-Host "Finalise new action code..."
sam install actions

# Complete
Write-Host "New actions installed successfully."