param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force

$tenantID = Get-Content .\MSGraphTenantID.txt -Raw
$clientID = Get-Content .\MSGraphClientID.txt -Raw
$certificateThumbprint = Get-Content .\MSGraphCertificateThumbprint.txt -Raw
Connect-MgGraph -ClientId $clientID -TenantId $tenantID -CertificateThumbprint $certificateThumbprint -NoWelcome

Set-EntraUserPassword -UserId $UserID -Password $securePassword -ErrorAction SilentlyContinue
if ($? -eq $false) {
  echo "Error setting password - trying to create user first.
  $PasswordProfile = @{
    Password = $Password
  }
  #DisplayName = "John Smith"
  #MailNickName = left of @
  #New-MgUser -DisplayName $UserID -PasswordProfile $PasswordProfile -AccountEnabled -MailNickName $UserID -UserPrincipalName $UserID
}

exit 1
