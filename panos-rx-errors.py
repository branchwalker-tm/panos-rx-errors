import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Config
 
HOST = 'IP_OR_HOSTNAME'           # Replace with your firewall's IP or hostname
INTERFACE_NAME = 'INTERFACE_NAME' # Replace with your interface name
API_KEY = 'YOUR_API_KEY'          # Replace with your actual API key

# Construct the API URL ---
api_command = f"<show><counter><interface>{INTERFACE_NAME}</interface></counter></show>" # Replace with your actual interface name

# URL-encode the XML command
encoded_api_command = urllib.parse.quote_plus(api_command)
url = f"https://{HOST}/api/?key={API_KEY}&type=op&cmd={encoded_api_command}"

# Make the API Call
try:
    # verify=False should only be used for testing. For production, set verify=True and ensure proper CAs.
    response = requests.get(url, verify=False)
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

    xml_data = response.text

    # Parse the XML Response
    root = ET.fromstring(xml_data)

    # Check for API success status first
    status = root.get('status')
    if status != 'success':
        error_msg = root.find('.//msg').text if root.find('.//msg') is not None else 'Unknown error'
        print(f"API call failed: Status='{status}', Message='{error_msg}'")
    else:
        # Define the XPath to the rx-error value
        # Make sure the XPath matches your XML structure exactly
        # For interface receive errors: /response/result/hw/entry/port/rx-error
        xpath_expression = f".//entry[name='{INTERFACE_NAME}']/port/rx-error" # Use .// to find anywhere, or specify full path

        # Find the element using XPath
        rx_error_element = root.find(xpath_expression)

        if rx_error_element is not None:
            rx_error_value = rx_error_element.text
            print(f"Interface {INTERFACE_NAME} rx-errors: {rx_error_value}")
        else:
            print(f"Could not find rx-error for {INTERFACE_NAME} using XPath: {xpath_expression}")
            print("Raw XML response for debugging:\n", xml_data)

except requests.exceptions.RequestException as e:
    print(f"An HTTP request error occurred: {e}")
except ET.ParseError as e:
    print(f"An XML parsing error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
