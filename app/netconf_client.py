from ncclient import manager
from ncclient.operations import RPCError
import logging

class NetconfClient:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.logger = logging.getLogger(f'{__name__}.{host}')

    def connect(self):
        if self.connection is not None:
            self.logger.warning("Already connected to device")
            return True
        
        try:
            self.logger.info(f"Connecting to {self.host}:{self.port}")
            
            self.connection = manager.connect(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                hostkey_verify=False,
                device_params={'name': 'default'},
                timeout=30
            )
            
            self.logger.info(f"Successfully connected to {self.host}")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection to {self.host} failed: {e}")
            self.connection = None
            raise  

    def get_capabilities(self):
        if self.connection is None:
            raise ConnectionError(f"Not connected to device {self.host}")
        
        capabilities = list(self.connection.server_capabilities)
        return capabilities

    def get_config(self, source="running", filter_xml=None):
        if self.connection is None:
            raise ConnectionError(f"Not connected to device {self.host}")
        
        try:
            self.logger.info(f"Retrieving configuration for {self.host}")

            if filter_xml:
                response = self.connection.get_config(source=source, filter=filter_xml)
            else:
                response = self.connection.get_config(source=source)

            return response.data_xml
        
        except RPCError as e:
            self.logger.error(f"get_config failed: {e.message}")
            raise
        
        except Exception as e:
            self.logger.error(f"Unexpected error in get_config: {e}")
            raise

    def edit_config(self, config_xml, target='candidate'):
        if self.connection is None:
            raise ConnectionError(f"Not connected to device {self.host}")
        
        try:
            self.logger.info(f"Updating configuration for {self.host}")
            response = self.connection.edit_config(target=target, config=config_xml)
            self.logger.info("Configuration update successful")
            return True
        
        except RPCError as e:
            self.logger.error(f"Configuration updated failed: {e.message}")
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error happened: {e}")
            raise

    def commit(self):
        if self.connection is None:
            raise ConnectionError(f"Not connected to device {self.host}")
        
        try:
            self.logger.info("Committing configuration")
            self.connection.commit()
            self.logger.info("Configuration committed successfully")
            return True
            
        except RPCError as e:
            self.logger.error(f"Commit failed: {e.message}")
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error happened: {e}")
            raise

    def close(self):
        if self.connection is None:
            raise ConnectionError(f"Not connected to device {self.host}")
        
        try:
            self.connection.close_session()
            self.connection = None
        except Exception as e:
            print(f"Unexpected error happened while closing the connection: {e}")
            raise

