param ([string]$UserID, [string]$Password)

#Connect-Entra -Scopes 'User.ReadWrite.All'
$accessToken = Get-Content .\MSGraphAccessToken.txt -Raw
Connect-MgGraph -AccessToken ($accessToken | ConvertTo-SecureString -AsPlainText -Force) -Scopes 'User.ReadWrite.All'

$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force
Set-EntraUserPassword -UserId $UserID -Password $securePassword
exit 1
