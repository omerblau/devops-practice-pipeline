$wt = "$env:LOCALAPPDATA\Microsoft\WindowsApps\wt.exe"

& $wt `
  split-pane --vertical --profile "PowerShell" --commandline "docker logs -f devops-practice-pipeline-db-1" `
  ; split-pane --vertical --profile "PowerShell" --commandline "docker logs -f devops-practice-pipeline-backend-1" `
  ; split-pane --vertical --profile "PowerShell" --commandline "docker logs -f devops-practice-pipeline-frontend-1"
