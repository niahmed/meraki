import meraki
import csv
import sys

def main():
    # Prompt the user for API Key, Org ID, Network Name, and CSV file
    api_key = input("Enter your Meraki Dashboard API key: ").strip()
    network_id = input("Enter the network ID: ").strip()  # User provides the specific network ID
    csv_file = input("Enter the path to the CSV file containing NAT rules: ").strip()

    # Initialize the Meraki Dashboard API
    dashboard = meraki.DashboardAPI(api_key, print_console=False)

    # Read NAT rules from CSV file
    rules = []
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                allowed_inbound_list = []
                
                # Parse 'allowedInbound' from the CSV into the required structure
                if row["allowedInbound"]:
                    allowed_inbound_entries = row["allowedInbound"].split(";")
                    for entry in allowed_inbound_entries:
                        parts = entry.split("|")
                        allowed_inbound = {
                            "protocol": parts[0].strip(),
                            "destinationPorts": parts[1].strip().split(","),
                            "allowedIps": parts[2].strip().split(",")
                        }
                        allowed_inbound_list.append(allowed_inbound)

                # Build the rule structure
                rule = {
                    "name": row["name"],
                    "publicIp": row["publicIp"],
                    "lanIp": row["lanIp"],
                    "uplink": row.get("uplink", "internet1"),  # Optional Uplink (default: "internet1")
                    "allowedInbound": allowed_inbound_list
                }

                rules.append(rule)
    
    except FileNotFoundError:
        print(f"CSV file '{csv_file}' not found.")
        sys.exit(1)
    except KeyError as e:
        print(f"Missing column in CSV file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during CSV parsing: {e}")
        sys.exit(1)

    # Update 1:1 NAT rules for the provided network_id
    try:
        response = dashboard.appliance.updateNetworkApplianceFirewallOneToOneNatRules(
            network_id,
            rules=rules
        )
        print(f"Successfully updated NAT rules for network ID '{network_id}'.")
        print("Response from Meraki API:", response)
    except meraki.exceptions.APIError as e:
        print(f"Error updating NAT rules: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
