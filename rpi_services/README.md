## Native Installation


### System Services
```bash

# Wifi check LED
sudo cp check_wifi.service /etc/systemd/system/
cp check_wifi.py /home/pi/
sudo systemctl enable check_wifi.service
sudo systemctl start check_wifi.service

# Wifi MicroSD config
sudo cp wifi_setup.service  /etc/systemd/system/
cp wifi_setup.sh /boot/
cp wifi_config.txt /boot/
sudo systemctl enable wifi_setup.service
sudo systemctl start wifi_setup.service

# FossBot App service
sudo cp fossbot_app.service /etc/systemd/system/
sudo systemctl enable fossbot_app.service
sudo systemctl start fossbot_app.service
```