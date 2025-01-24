param ([string]$UserID, [string]$Password)
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force

$tenantID = Get-Content .\MSGraphTenantID.txt -Raw
$clientID = Get-Content .\MSGraphClientID.txt -Raw
$certificateThumbprint = Get-Content .\MSGraphCertificateThumbprint.txt -Raw
Connect-MgGraph -ClientId $clientID -TenantId $tenantID -CertificateThumbprint $certificateThumbprint -NoWelcome

Try {
  Set-EntraUserPassword -UserId $UserID -Password $securePassword -ErrorAction Stop
} Catch [Exception] {
  echo "Error setting password - trying to create user first."
  $PasswordProfile = @{
    Password = $Password
  }
  #DisplayName = "John Smith"
  $MailNickName = $UserID.Split("@")[0]
  Try {
    New-MgUser -DisplayName $MailNickName -PasswordProfile $PasswordProfile -AccountEnabled -MailNickName $MailNickName -UserPrincipalName $UserID -ErrorAction Stop
  } Catch [Exception] {
    echo "Error creating Entra ID user: $UserID."
    exit 1
  }
}
