import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Config

HOST = 'IP_OR_HOSTNAME'
INTERFACE_NAME = 'INTERFACE_NAME' # Replace with your preferred default interface nam (to be used as a fallback if interface list is not able to be retrieved)
API_KEY = 'YOUR_API_KEY'          # Replace with your actual API key

# Find all interface names first
def get_panos_interfaces(hostname, api_key):
    # Store the names in an array
    interface_names = []

    # Build API command
    cmd = '<show><interface>all</interface></show>'
    url = f"https://{HOST}/api/?type=op&cmd={cmd}&key={API_KEY}"

    try:
        # Send the API request
        response = requests.get(url, verify=False)

        # Check for a successful response
        response.raise_for_status()

        # Parse the response
        root = ET.fromstring(response.content)

        # If the API response is correct, add each interface name to the array
        status = root.get('status')
        if status == 'success':
            for interface_entry in root.findall(".//result/ifnet/entry"):
                name = interface_entry.findtext('name')
                if name:
                    interface_names.append(name)
        else:
            error_msg = root.findtext(".//msg/text")
            print(f"API call failed. Status: {status}. Error: {error_msg if error_msg else 'Unknown error.'}")

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.ConnectionError as err:
        print(f"Connection error occurred: {err}. Please check hostname and network connectivity.")
    except requests.exceptions.Timeout as err:
        print(f"Timeout error occurred: {err}. The request took too long.")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
    except ET.ParseError as err:
        print(f"Failed to parse XML response: {err}. Response content: {response.content}")

    return interface_names

# Get all interface names
interfaces = get_panos_interfaces(HOST, API_KEY)

# UNCOMMENT FOR DEBUGGING - This just lists the interface names we get to be sure we got them
# if interfaces:
#    for i, interface in enumerate(interfaces):
#        print(f"{i+1}. {interface}")
# else:
#    print("\nNo interfaces found or an error occurred during retrieval.")

# Construct the RX error API URL
api_command = f"<show><counter><interface>{INTERFACE_NAME}</interface></counter></show>"

# URL-encode the XML command
encoded_api_command = urllib.parse.quote_plus(api_command)
url = f"https://{HOST}/api/?key={API_KEY}&type=op&cmd={encoded_api_command}"

for interface_name in interfaces:
    # Make the RX Error API Call
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
