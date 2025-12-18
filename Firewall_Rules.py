import csv
import sys
from meraki import DashboardAPI

# Function to read CSV and parse rules
def parse_csv(file_path):
    rules = []

    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row['policy'] or not row['protocol'] or not row['srcCidr'] or not row['destCidr']:
                    raise ValueError(f"Row is missing required fields: {row}")

                # Build the rule dictionary
                rule = {
                    "comment": row.get('comment', ''),
                    "policy": row['policy'].strip().lower(),
                    "protocol": row['protocol'].strip().lower(),
                    "srcCidr": row['srcCidr'].strip(),
                    "srcPort": row.get('srcPort', 'any').strip(),
                    "destCidr": row['destCidr'].strip(),
                    "destPort": row.get('destPort', 'any').strip(),
                }

                rules.append(rule)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during CSV parsing: {e}")
        sys.exit(1)

    return rules

# Function to update the L3 Firewall Rules
def update_firewall_rules(api_key, network_id, rules):
    dashboard = DashboardAPI(api_key)

    try:
        # Update the Layer 3 firewall rules
        response = dashboard.appliance.updateNetworkApplianceFirewallL3FirewallRules(
            networkId=network_id,  # Pass the network ID here
            rules=rules,
        )
        print("L3 Firewall Rules updated successfully!")
        return response
    except Exception as e:
        print(f"Error updating L3 Firewall Rules: {e}")
        sys.exit(1)

# Main entry point
if __name__ == "__main__":
    # Prompt for API key and Network ID
    API_KEY = input("Enter your Meraki Dashboard API Key: ").strip()
    NETWORK_ID = input("Enter the Network ID: ").strip()
    CSV_FILE = input("Enter the path to the CSV file (e.g., firewall_rules.csv): ").strip()

    # Parse rules from CSV
    print(f"Parsing rules from CSV file: {CSV_FILE}...")
    firewall_rules = parse_csv(CSV_FILE)

    print(f"Parsed {len(firewall_rules)} firewall rules from the CSV file.")

    # Add a default rule to allow traffic in case it's not already defined in the CSV (Meraki requires it)
    default_rule = {
        "comment": "Default rule",
        "policy": "allow",
        "protocol": "any",
        "srcCidr": "any",
        "srcPort": "any",
        "destCidr": "any",
        "destPort": "any",
    }
    firewall_rules.append(default_rule)

    # Output the rules for debugging
    print("Firewall rules to be applied:")
    for rule in firewall_rules:
        print(rule)

    # Update the firewall rules in the network
    print("Updating L3 firewall rules...")
    update_firewall_rules(API_KEY, NETWORK_ID, firewall_rules)
