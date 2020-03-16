# Pi details
$Password = "RASPBERRY"
$User = "pi"
$ComputerName = "192.168.0.27"

# SSH connection
$secpasswd = ConvertTo-SecureString $Password -AsPlainText -Force
$Credentials = New-Object System.Management.Automation.PSCredential($User, $secpasswd)
$SessionID = New-SSHSession -ComputerName $ComputerName -Credential $Credentials #Connect Over SSH

Write-Host "[DAN] Install new action code..."

# Push changes to github
Write-Host "[DAN] Pushing action code to github..."
git add . 
git commit -m "debug" 
git push
Write-Host "[DAN] Done."

# Login to pi and delete the old skills
Write-Host "[out] Deleting old skill from Pi..."
$Command = "sudo rm -r /var/lib/snips/skills/WheresMyGlassesFrontend/"
Invoke-SSHCommand -Index $sessionid.sessionid -Command $Command # Invoke Command Over SSH
Write-Host "[DAN] Done."

# Download the new action code with Sam
Write-Host "[DAN] Downloading new actions to pi..."
sam install actions
Write-Host "[DAN] Done."

# Login to pi and change permissions
Write-Host "[DAN] Setting new action code permissions..."
$Command = "sudo chmod +x /var/lib/snips/skills/WheresMyGlassesFrontend/action-FrontendManager.py"
Invoke-SSHCommand -Index $sessionid.sessionid -Command $Command # Invoke Command Over SSH

# Reinstall actions
Write-Host "[DAN] Finalise new action code..."
sam install actions
Write-Host "[DAN] Done."

# Complete
Write-Host "[DAN] New actions installed successfully."