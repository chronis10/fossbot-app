## Diagnostic tool for the physical FossBot
If the FossBot app already running run the following command in the /home/pi
```bash docker compose down```

Transfer all the files from the this directory in a new directory inside the FossBot
```bash cd /home/pi
        mkdir diagnostics
        cd  diagnostics
        wget https://raw.githubusercontent.com/chronis10/fossbot-app/raw/master/blockly_server/utils/sound_effects/proccesing.mp3
        
```