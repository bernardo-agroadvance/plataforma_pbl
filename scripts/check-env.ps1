# Mostra as variáveis esperadas nos .env.example de cada app
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$files = @(
  "..\fastapi_backend\.env.example",
  "..\pbl_admin\.env.example",
  "..\frontend\.env.example"
)
foreach ($f in $files) {
  $path = Join-Path $Here $f
  Write-Host "`n---- $f ----"
  if (Test-Path $path) {
    Get-Content $path | Where-Object { $_ -match '^[A-Z0-9_]+=' }
  } else {
    Write-Host "arquivo não encontrado"
  }
}
