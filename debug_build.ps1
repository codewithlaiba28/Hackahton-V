$logFile = "docker_build.log"
docker build --progress=plain -t fte-backend ./backend 2>&1 | Tee-Object -FilePath $logFile
