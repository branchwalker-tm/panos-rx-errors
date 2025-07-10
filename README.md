# panos-rx-errors
A simple python script that pulls logical and hardware receive errors on CPU from the PANOS XML API

## How to use

1. You will need to generate your API key before use, and add it to the `API_KEY` variable
`curl -H "Content-Type: application/x-www-form-urlencoded" -X POST https://<firewall>/api/?type=keygen -d 'user=<user>&password=<password>'`

2. Add your firewall's IP address or hostname to the variable `HOST`

3. Add your interface name to the `INTERFACE_NAME` variable

4. You will also need to make sure `requests` is installed
`pip install requests`

5. Run the script: `python panos-rx-errors.py` 


