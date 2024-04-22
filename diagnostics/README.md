## Diagnostic tool for the physical FossBot
If the FossBot app already running run the following command in the /home/pi

```bash
 docker compose down
 ```

Transfer all the files from the this directory in a new directory inside the FossBot

Create the diagnostics directory
```bash 
cd /home/pi
mkdir diagnostics
cd  diagnostics
```

Download the diagnostics files
```bash 
wget https://raw.githubusercontent.com/chronis10/fossbot-app/master/diagnostics/admin_parameters.yaml
wget https://raw.githubusercontent.com/chronis10/fossbot-app/master/diagnostics/diagnostics.py
wget https://raw.githubusercontent.com/chronis10/fossbot-app/master/diagnostics/r2d2.mp3
wget https://raw.githubusercontent.com/chronis10/fossbot-app/master/diagnostics/run_diagnostics.sh
```
First run
```bash
chmod +x run_diagnostics.sh
```

Start the diagnostics container
```bash
./run_diagnostics.sh
```

Inside the container run the diagnostics script
```bash
python3 diagnostics.py
```
