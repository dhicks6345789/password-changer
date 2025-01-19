param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force

$tenantID = Get-Content .\MSGraphTenantID.txt -Raw
$clientID = Get-Content .\MSGraphClientID.txt -Raw
$certificateThumbprint = Get-Content .\MSGraphCertificateThumbprint.txt -Raw
Connect-MgGraph -ClientId $clientID -TenantId $tenantID -CertificateThumbprint $certificateThumbprint -NoWelcome

#Set-EntraUserPassword -UserId $UserID -Password $securePassword -ErrorAction SilentlyContinue
Set-EntraUserPassword -UserId $UserID -Password $securePassword -ErrorVariable setPasswordError

echo "Bananas!"
#echo $error.Status

echo $setPasswordError

exit 1
