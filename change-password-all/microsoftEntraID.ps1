param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force
Connect-Entra -Scopes 'User.ReadWrite.All'
Set-EntraUserPassword -UserId $UserID -Password $securePassword
