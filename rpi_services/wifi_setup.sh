#!/bin/bash

# Path to the WiFi configuration file
CONFIG_FILE="/boot/wifi_config.txt"
WPA_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"

# Check if the configuration file exists
if [ -f "$CONFIG_FILE" ]; then
    echo "Reading WiFi credentials from $CONFIG_FILE..."

    # Source the credentials from the file
    source "$CONFIG_FILE"
    key_mgmt="${key_mgmt:-WPA-PSK}"
    region="${region:-GR}"
    
    # Determine if the user specified 'None' for both `psk` and `key_mgmt`
    if [[ "$key_mgmt" == "None" && "$psk" == "None" ]]; then
        echo "Detected open network configuration. Setting key_mgmt to NONE."
        key_mgmt="NONE"
        unset psk  # Remove the psk variable since it shouldn't be used for open networks
    fi
    
    # Create the wpa_supplicant.conf file with the new credentials
    sudo bash -c "cat > $WPA_CONF" << EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=$region

network={
    ssid="$ssid"
    key_mgmt=$key_mgmt
    $( [ "$key_mgmt" != "NONE" ] && echo "psk=\"$psk\"" )
}
EOF

    echo "Updated $WPA_CONF with new WiFi credentials."

    # Restart the WiFi service to apply changes
    sudo wpa_cli -i wlan0 reconfigure

    echo "WiFi configuration applied successfully."
else
    echo "Configuration file $CONFIG_FILE not found!"
fi
