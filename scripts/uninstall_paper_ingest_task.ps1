[CmdletBinding()]
param([switch]$WhatIf)

$ErrorActionPreference = 'Stop'
if ($WhatIf) { '{"TaskName":"PaperDailyIngest","Action":"schtasks /Delete /F"}'; exit 0 }
& schtasks.exe /Delete /TN PaperDailyIngest /F
exit $LASTEXITCODE
