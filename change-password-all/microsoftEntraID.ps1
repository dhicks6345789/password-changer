param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force

$tenantID = Get-Content .\MSGraphTenantID.txt -Raw
$clientID = Get-Content .\MSGraphClientID.txt -Raw
$certificateThumbprint = Get-Content .\MSGraphCertificateThumbprint.txt -Raw
Connect-MgGraph -ClientId $clientID -TenantId $tenantID -CertificateThumbprint $certificateThumbprint -NoWelcome

# Set-EntraUserPassword -UserId $UserID -Password $securePassword -ErrorAction SilentlyContinue
Set-EntraUserPassword -UserId $UserID -Password $securePassword
if ($? -eq $false) {
  echo "Error setting password - trying to create user first."
  $PasswordProfile = @{
    Password = $Password
  }
  #DisplayName = "John Smith"
  $MailNickName = $UserID.Split("@")[0]
  New-MgUser -DisplayName $MailNickName -PasswordProfile $PasswordProfile -AccountEnabled -MailNickName $MailNickName -UserPrincipalName $UserID
  if ($? -eq $false) {
    echo "Error creating Entra ID user: $UserID."
    exit 1
  }
}
