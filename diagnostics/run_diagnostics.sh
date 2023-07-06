#!/bin/bash
echo "Running diagnostics on physical FossBot..."
echo "Starting diagnostics container..."
docker run -it --rm --privileged --name fossbit-diagnostics -w / -v "${PWD}"/diagnostics.py:/diagnostics.py -v "${PWD}"/admin_parameters.yaml:/admin_parameters.yaml -v "${PWD}"/proccesing:/proccesing.mp3 --entrypoint /bin/bash chronis10/fossbot_blockly_phy:latest
echo "Diagnostics complete."
echo "Done."