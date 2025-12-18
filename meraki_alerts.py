import meraki

# Variables for Grafana Oncall Webhook
name = 'grafana-oncall'
url = 'https://a-prod-us-central-0.grafana.net/integrations/v1/formatted_webhook/Zaj725UJMEW6NpX3rlF7ug5L3/'

# Grafana Oncall Webhook URL in Base64
webhook_id = 'aHR0cHM6Ly9hLXByb2QtdXMtY2VudHJhbC0wLmdyYWZhbmEubmV0L2ludGVncmF0aW9ucy92MS9mb3JtYXR0ZWRfd2ViaG9vay9aYWo3MjVVSk1FVzZOcFgzcmxGN3VnNUwzLw=='

# Email for Meraki alerts
noc_email = 'meraki_noc_ingest_dl@altourage.com'

# Prompt user to enter API key
api_key = input('Enter Meraki API key: ')

# Instantiate Meraki client
dashboard = meraki.DashboardAPI(api_key)

# Get list of organizations and print IDs and names
orgs = dashboard.organizations.getOrganizations()
for org in orgs:
    print(f'Organization ID: {org["id"]}, Name: {org["name"]}')

# Configure alerts for each network to be sent to a specific email
for org in orgs:
    networks = dashboard.organizations.getOrganizationNetworks(org['id'])
    for network in networks:
        print(f'Configuring alerts for Network ID: {network["id"]}, Name: {network["name"]}')

        alert_settings = {
            'defaultDestinations': {
                'emails': [noc_email],
                'httpServerIds': [webhook_id]
            },
            'alerts': [
                {'type': 'settingsChanged', 'enabled': False},
                {'type': 'dhcpNoLeases', 'enabled': True},
                {'type': 'ipConflict', 'enabled': False},
                {'type': 'rogueDhcp', 'enabled': True},
                {'type': 'rogueAp', 'enabled': False},
                {'type': 'gatewayDown', 'enabled': True, 'filters': {'timeout': 5}, 'allDevices': True},
                {'type': 'repeaterDown', 'enabled': True, 'filters': {'timeout': 5}, 'allDevices': True},
                {'type': 'applianceDown', 'enabled': True, 'filters': {'timeout': 5}, 'allDevices': True},
                {'type': 'switchDown', 'enabled': True, 'filters': {'timeout': 5}, 'allDevices': True},
                {'type': 'powerSupplyDown', 'enabled': True, 'allDevices': True},
            ]
        }

        try:
            dashboard.networks.updateNetworkAlertsSettings(network['id'], **alert_settings)
            dashboard.networks.createNetworkWebhooksHttpServer(network['id'], name, url, payloadTemplate={'payloadTemplateId': 'wpt_00001', 'name': 'Meraki (included)'})
        except Exception as e:
            print(f"An error occurred for Network ID: {network['id']}. Error: {str(e)}")
            continue
