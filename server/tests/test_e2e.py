import pytest
import requests

BASE_URL = "http://localhost:5000/api"

@pytest.mark.e2e
class TestEndToEnd:
    def test_device_discovery(self):

        response = requests.post(f"{BASE_URL}/discover")
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'success'
        assert 'discovered' in data
        assert data['discovered'] == 2  # router-01 and switch-01
        assert 'devices' in data
        assert len(data['devices']) == 2
        assert 'timestamp' in data

        for device in data['devices']:
            assert 'hostname' in device
            assert 'ip' in device
            assert 'port' in device
            assert 'vendor' in device
            assert 'status' in device

        statuses = [device['status'] for device in data['devices']]
        assert 'connected' in statuses

    def test_device_status_success(self):

        response = requests.get(f"{BASE_URL}/router-01/status")

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'success'
        assert data['hostname'] == 'router-01'
        assert data['connection_success'] == True
        assert 'capabilities' in data
        assert len(data['capabilities']) > 0
        assert 'running_config' in data

        # Verify it's JSON with interfaces
        assert 'interfaces' in data['running_config']
        assert isinstance(data['running_config']['interfaces'], list)
        assert len(data['running_config']['interfaces']) > 0

        # Verify interface structure
        first_interface = data['running_config']['interfaces'][0]
        assert 'name' in first_interface
        assert 'type' in first_interface
        assert 'enabled' in first_interface

        assert 'device_info' in data

        assert 'ip' in data['device_info']
        assert 'port' in data['device_info']
        assert 'vendor' in data['device_info']

    def test_device_not_found(self):

        response = requests.get(f"{BASE_URL}/unknown-device/status")

        assert response.status_code == 404
        data = response.json()

        assert data['status'] == 'error'
        assert 'message' in data
        assert 'not found' in data['message'].lower()

    def test_device_conf_success(self):

        payload = {
            "interface_name": "GigabitEthernet0/3",
            "ip_address": "10.0.0.100",
            "subnet_mask": "255.255.255.0"
        }

        response = requests.post(
            f"{BASE_URL}/router-01/interface",
            json=payload
        )
        assert response.status_code == 200

        data = response.json()
        assert data['success'] == True
        assert 'message' in data
        assert 'GigabitEthernet0/3' in data['message']
        assert '10.0.0.100' in data['message']
        assert data['hostname'] == 'router-01'

    def test_device_conf_missing_param(self):

        payload = {
            "interface_name": "GigabitEthernet0/4",
            "ip_address": "10.0.0.200"
        }

        response = requests.post(
            f"{BASE_URL}/router-01/interface",
            json=payload
        )
        assert response.status_code == 400

        data = response.json()
        assert data['status'] == 'error'
        assert 'message' in data
        assert 'Missing required fields' in data['message']

