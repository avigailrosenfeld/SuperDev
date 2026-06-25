# הכנס את ה-token שלך ב-.env.local (לא עולה ל-GitHub)
# פורמט: AAD_TOKEN=eyJ0eXAi...

$envFile = "$PSScriptRoot\.env.local"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^AAD_TOKEN=(.+)$") { $token = $Matches[1] }
    }
} else {
    Write-Error "חסר קובץ .env.local — צור אותו עם AAD_TOKEN=<token שלך>"
    exit 1
}

docker stop superdev-chat 2>$null
docker rm superdev-chat 2>$null
docker build -f Dockerfile.chat -t superdev-chat .
docker run -d --name superdev-chat -p 8080:8080 -e "AAD_TOKEN=$token" superdev-chat

Write-Host "SuperDev chat running at http://localhost:8080"
