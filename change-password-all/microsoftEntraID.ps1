param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force

$accessToken = Get-Content .\MSGraphAccessToken.txt -Raw
echo $accessToken
$secureAccessToken = ConvertTo-SecureString $accessToken -AsPlainText -Force

#Connect-Entra -Scopes 'User.ReadWrite.All'
Connect-MgGraph -AccessToken $secureAccessToken -Scopes 'User.ReadWrite.All'

Set-EntraUserPassword -UserId $UserID -Password $securePassword
exit 1
