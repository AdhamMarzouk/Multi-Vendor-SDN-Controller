from .netconf_client import NetconfClient
import yaml

class sdn_controller:
    def __init__(self, inventory_path = 'inventory/devices.yaml'):
        self.inventory_path = inventory_path
        self.devices = {}
        self._load_inventory()

    def discover_devices(self):
        results = {}

        for hostname, device_info in self.devices.items():
            try:
                client = NetconfClient(
                    host=device_info['ip'],
                    port=device_info['port'],
                    username=device_info['username'],
                    password=device_info['password']
                )

                client.connect()
                capabilities = client.get_capabilities()
                client.close()

                results[hostname] = {
                    'success': True,
                    'message': 'Device discovered successfully',
                    'capabilities': capabilities
                }

            except Exception as e:
                results[hostname] = {
                    'success': False,
                    'message': f'Discovery failed: {str(e)}',
                    'capabilities': []
                }

        return results

    def get_device_count(self):
        return len(self.devices)

    def get_device_status(self, hostname):
        if hostname not in self.devices:
            raise KeyError(f"Device '{hostname}' not found in inventory")

        device_info = self.devices[hostname]

        client = NetconfClient(
            host=device_info['ip'],
            port=device_info['port'],
            username=device_info['username'],
            password=device_info['password']
        )

        client.connect()
        capabilities = client.get_capabilities()
        running_config = client.get_config(source='running')
        client.close()

        return {
            'hostname': hostname,
            'connection_success': True,
            'capabilities': capabilities,
            'running_config': running_config,
            'device_info': device_info
        }

    def configure_interface(self, hostname, interface_name, ip_address, subnet_mask):
        if hostname not in self.devices:
            raise KeyError(f"Device '{hostname}' not found in inventory")

        config_xml = self._build_config_xml(interface_name, ip_address, subnet_mask)

        device_info = self.devices[hostname]

        client = NetconfClient(
            host=device_info['ip'],
            port=device_info['port'],
            username=device_info['username'],
            password=device_info['password']
        )

        client.connect()
        client.edit_config(config_xml, target='candidate')
        client.commit()
        client.close()

        return {
            'success': True,
            'message': f'Interface {interface_name} configured with IP {ip_address}/{subnet_mask}',
            'hostname': hostname
        }
    
    def _load_inventory(self):
        with open(self.inventory_path, 'r') as file:
            inventory_data = yaml.safe_load(file)

        devices_list = inventory_data['devices']
        self.devices = {}

        for device in devices_list:
            hostname = device['hostname']
            self.devices[hostname] = {
                'ip': device['ip'],
                'port': device['port'],
                'username': device['username'],
                'password': device['password'],
                'vendor': device['vendor'],
                'description': device['description']
            }

    def _build_config_xml(self, interface_name, ip_address, subnet_mask):
        config_xml = f'''<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>{interface_name}</name>
            <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
            <enabled>true</enabled>
            <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                <address>
                    <ip>{ip_address}</ip>
                    <netmask>{subnet_mask}</netmask>
                </address>
            </ipv4>
        </interface>
    </interfaces>
</config>'''

        return config_xml

