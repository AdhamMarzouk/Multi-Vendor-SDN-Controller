import pytest
from unittest.mock import MagicMock, patch
from app.netconf_client import NetconfClient


@pytest.fixture
def device_params():
    return{
        'host': '127.0.0.1',
        'port': 8300,
        'username': 'admin',
        'password': 'admin'
    }

@pytest.fixture
def netconf_client(device_params):
    client = NetconfClient(**device_params)
    yield client

    if client.connection is not None:
        client.close()


class TestNetconfClient:   

    def test_initialization(self, netconf_client, device_params):
        assert netconf_client.host == device_params['host']
        assert netconf_client.port == device_params['port']
        assert netconf_client.username == device_params['username']
        assert netconf_client.password == device_params['password']
        assert netconf_client.connection is None  
    
    @patch('app.netconf_client.manager')
    def test_connect(self, mock_manager, netconf_client):

        mock_connection = MagicMock()
        mock_connection.session_id = '12345'
        mock_manager.connect.return_value = mock_connection
        
        result = netconf_client.connect()
        
        assert result is True
        assert netconf_client.connection is mock_connection
        
        # Verify connect was called with correct parameters
        mock_manager.connect.assert_called_once()
        call_args = mock_manager.connect.call_args
        assert call_args.kwargs['host'] == netconf_client.host
        assert call_args.kwargs['port'] == netconf_client.port
        assert call_args.kwargs['username'] == netconf_client.username

    def test_get_capabilities_success(self, netconf_client):
        mock_connection = MagicMock()
        mock_connection.server_capabilities = {
            'urn:ietf:params:netconf:base:1.0',
            'urn:ietf:params:xml:ns:yang:ietf-interfaces'
        }

        netconf_client.connection = mock_connection
        capabilities = netconf_client.get_capabilities()

        assert isinstance(capabilities, list)
        assert len(capabilities) == 2
        assert 'urn:ietf:params:netconf:base:1.0' in capabilities and 'urn:ietf:params:xml:ns:yang:ietf-interfaces' in capabilities

    def test_get_config(self, netconf_client):

        mock_connection = MagicMock()
        mock_reply = MagicMock()
        mock_reply.data_xml = '<config>test</config>'
        mock_connection.get_config.return_value = mock_reply
        netconf_client.connection = mock_connection
        
        config = netconf_client.get_config(source='running')
        
        assert config == '<config>test</config>'

    def test_edit_configs(self, netconf_client):

        mock_connection = MagicMock()
        netconf_client.connection = mock_connection
        
        config_xml = '<config>test</config>'
        result = netconf_client.edit_config(config_xml, target='candidate')
        
        assert result is True
        
    def test_commit(self, netconf_client):

        mock_connection = MagicMock()
        netconf_client.connection = mock_connection
        
        result = netconf_client.commit()
        
        assert result is True
        
    def test_close(self, netconf_client):

        mock_connection = MagicMock()
        netconf_client.connection = mock_connection
        netconf_client.close()
        
        assert netconf_client.connection is None

    