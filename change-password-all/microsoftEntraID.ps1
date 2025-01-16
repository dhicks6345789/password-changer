param ([string]$UserID, [string]$Password)

#Connect-Entra -Scopes 'User.ReadWrite.All'
$accessToken = <paste-your-token-here>
Connect-MgGraph -AccessToken ($accessToken | ConvertTo-SecureString -AsPlainText -Force)

$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force
Set-EntraUserPassword -UserId $UserID -Password $securePassword
exit 1
