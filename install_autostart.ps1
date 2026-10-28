# 注册 wxbot-mini 开机自启（当前用户，登录后自动运行 run.py）
# 用法：右键"使用 PowerShell 运行"，或在 PowerShell 里执行本脚本
# 卸载：schtasks /Delete /TN wxbot-mini /F

$name = "wxbot-mini"
$py = (Get-Command python).Source
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$action = "cmd /c cd /d `"$root`" && `"$py`" run.py"

schtasks /Query /TN $name 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) { schtasks /Delete /TN $name /F | Out-Null }

schtasks /Create /TN $name /TR $action /SC ONLOGON /RL LIMITED /F
schtasks /Query /TN $name /FO LIST
