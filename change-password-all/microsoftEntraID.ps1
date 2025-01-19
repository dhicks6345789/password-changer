param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force

#$accessToken = Get-Content .\MSGraphAccessToken.txt -Raw
#$secureAccessToken = ConvertTo-SecureString $accessToken -AsPlainText -Force

#Connect-Entra -Scopes 'User.ReadWrite.All'
#Connect-MgGraph -AccessToken $secureAccessToken -NoWelcome

$tenantID = Get-Content .\MSGraphTenantID.txt -Raw
$clientID = Get-Content .\MSGraphClientID.txt -Raw
$certificateThumbprint = Get-Content .\MSGraphCertificateThumbprint.txt -Raw
Connect-MgGraph -ClientId $clientID -TenantId $tenantID -CertificateThumbprint $certificateThumbprint -NoWelcome

Set-EntraUserPassword -UserId $UserID -Password $securePassword
exit 1
