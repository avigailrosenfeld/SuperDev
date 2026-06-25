$envFile = "$PSScriptRoot\.env.local"
$token = ""

if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^AAD_TOKEN=(.+)$") { $token = $Matches[1] }
    }
} else {
    Write-Error "Missing .env.local - create it with AAD_TOKEN=<your token>"
    exit 1
}

if (-not $token) {
    Write-Error "AAD_TOKEN not found in .env.local"
    exit 1
}

docker stop superdev-chat 2>$null
docker rm superdev-chat 2>$null
docker build -f Dockerfile.chat -t superdev-chat .
docker run -d --name superdev-chat -p 8080:8080 -e AAD_TOKEN=$token superdev-chat

Write-Host "SuperDev running at http://localhost:8080"
