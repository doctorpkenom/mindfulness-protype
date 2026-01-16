$domain = "mindfulness-prototype.local"
$hostsFile = "$env:SystemRoot\System32\drivers\etc\hosts"

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator to update the hosts file."
    exit
}

$content = Get-Content $hostsFile
if ($content -match $domain) {
    Write-Host "Domain $domain already exists in hosts file." -ForegroundColor Yellow
}
else {
    Add-Content -Path $hostsFile -Value "127.0.0.1 $domain"
    Write-Host "Added $domain to hosts file." -ForegroundColor Green
    Write-Host "You can now access the app at http://$domain:5173" -ForegroundColor Green
}
