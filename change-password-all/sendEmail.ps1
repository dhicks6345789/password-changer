param ([string]$UserID, [string]$Password)

gam sendemail destination@email.com from useralias@domain.com mailbox user@domain.com subject "test subject" message "text body" ...

Connect-MgGraph -ClientId $clientID -TenantId $tenantID -CertificateThumbprint $certificateThumbprint -NoWelcome
