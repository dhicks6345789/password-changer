param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force

$tenantID = Get-Content .\MSGraphTenantID.txt -Raw
$clientID = Get-Content .\MSGraphClientID.txt -Raw
$certificateThumbprint = Get-Content .\MSGraphCertificateThumbprint.txt -Raw
Connect-MgGraph -ClientId $clientID -TenantId $tenantID -CertificateThumbprint $certificateThumbprint -NoWelcome

Set-EntraUserPassword -UserId $UserID -Password $securePassword -ErrorAction SilentlyContinue
if ($? -eq $false) {
  echo "Error setting password"
}

#echo $error.Status

echo "Oranges!"
echo $setPasswordError
echo "Bananas!"
echo $setPasswordError.Status

exit 1
