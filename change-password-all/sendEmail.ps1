param ([string]$UserID, [string]$Password)

$destinationEmailAddress = Get-Content .\NotificationsToEmailAddress.txt -Raw
$fromEmailAddress = Get-Content .\NotificationsFromEmailAddress.txt -Raw

gam sendemail $destinationEmailAddress from $fromEmailAddress mailbox $fromEmailAddress subject "User $UserID Password Change" message "User $UserID has had their password changed by the password changer utility."
