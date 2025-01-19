param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force

#$accessToken = Get-Content .\MSGraphAccessToken.txt -Raw
#$secureAccessToken = ConvertTo-SecureString $accessToken -AsPlainText -Force

#Connect-Entra -Scopes 'User.ReadWrite.All'
#Connect-MgGraph -AccessToken $secureAccessToken -NoWelcome

$clientID = Get-Content .\MSGraphClientID.txt -Raw
$tenantID = Get-Content .\MSGraphTenantID.txt -Raw
Connect-MgGraph -ClientId $clientID -TenantId $tenantID

Set-EntraUserPassword -UserId $UserID -Password $securePassword
exit 1
