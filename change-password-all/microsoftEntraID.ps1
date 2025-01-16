param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force
Set-EntraUserPassword -UserId $UserID -Password $securePassword
