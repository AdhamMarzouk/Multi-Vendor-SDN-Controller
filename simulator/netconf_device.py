import socket
import threading
import paramiko
import logging
import sys

# Set up logging so we can see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NetconfSimulator')


class NetconfDeviceSimulator:
    """
    Simulates a NETCONF-capable network device for testing purposes.
    
    This class creates an SSH server that implements enough of the NETCONF protocol
    to allow a controller to connect, retrieve configuration, and push changes.
    It doesn't actually configure any real networking - it just plays the role
    convincingly enough for development and testing.
    """
    
    def __init__(self, listen_address='127.0.0.1', listen_port=8300):
        """
        Initialize the simulator.
        
        Args:
            listen_address: The IP address to bind to (default localhost)
            listen_port: The port to listen on (default 8300 to avoid conflict with real NETCONF on 830)
        """
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.running = False
        
        # Generate an SSH host key - this is what makes our SSH server cryptographically valid
        # We use RSA with 2048 bits which is standard for SSH servers
        logger.info("Generating SSH host key (this may take a moment)...")
        self.host_key = paramiko.RSAKey.generate(2048)
        logger.info("Host key generated successfully")
        
        # This dictionary will store our fake device configuration
        # When a controller configures an interface, we'll store it here
        # When it requests configuration, we'll return what's stored here
        self.device_config = {
            'interfaces': {}
        }

    def start(self):
        """
        Start the NETCONF simulator server.
        
        This creates a TCP socket, binds it to the configured address and port,
        and enters a loop accepting incoming connections. Each connection is
        handled in a separate thread so we can serve multiple clients simultaneously.
        """
        
        # Create a TCP socket - this is the foundation of network communication
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # SO_REUSEADDR lets us restart the simulator immediately even if the port
        # is in TIME_WAIT state from a previous run - very useful during development
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to our address and port
        server_socket.bind((self.listen_address, self.listen_port))
        
        # Listen for incoming connections - the 5 means we can have up to 5 pending
        # connections waiting while we're busy handling others
        server_socket.listen(5)
        
        self.running = True
        logger.info(f"NETCONF simulator listening on {self.listen_address}:{self.listen_port}")
        logger.info("Waiting for connections from SDN controller...")
        
        try:
            # Main server loop - keep accepting connections until stopped
            while self.running:
                # Accept blocks until a client connects
                # client_socket is our communication channel to that specific client
                # client_address tells us who connected
                client_socket, client_address = server_socket.accept()
                logger.info(f"Received connection from {client_address}")
                
                # Handle each client in a separate thread so we don't block other connections
                # daemon=True means the thread will automatically die when the main program exits
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()
                
        except KeyboardInterrupt:
            logger.info("Simulator stopped by user")
        finally:
            # Clean shutdown - close the server socket
            server_socket.close()
            self.running = False
            logger.info("Simulator shut down")

    def _handle_client(self, client_socket):
        """
        Handle a single client connection.
        
        This method runs in its own thread for each connected client.
        It sets up the SSH session, authenticates the client, and then
        handles NETCONF protocol messages.
        
        Args:
            client_socket: The socket connected to the client
        """
        # Wrap the raw socket in Paramiko's SSH transport
        # This handles all the SSH protocol complexity for us
        transport = paramiko.Transport(client_socket)
        
        # Add our host key so the client can verify our identity
        transport.add_server_key(self.host_key)
        
        # Create a server interface that handles authentication
        # We'll define this class in a moment
        server = NetconfSSHServer()
        
        try:
            # Start the SSH server side of the connection
            # This does the SSH handshake, key exchange, encryption setup
            transport.start_server(server=server)
            
            # Wait for authentication to complete
            # The client sends username/password, we check it, respond with success/failure
            channel = transport.accept(timeout=20)
            
            if channel is None:
                logger.error("Client failed to open SSH channel")
                return
                
            logger.info("SSH channel established successfully")
            
            # Now we have an encrypted, authenticated SSH channel
            # Time to start the NETCONF protocol on top of it
            self._handle_netconf_session(channel)
            
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            # Always clean up the transport when done
            transport.close()

    def _handle_netconf_session(self, channel):
        """
        Handle the NETCONF protocol on an established SSH channel.

        This implements the NETCONF message exchange:
        1. Send our hello message advertising capabilities
        2. Receive client's hello message
        3. Process RPC requests and send responses
        4. Handle session termination

        Args:
            channel: The SSH channel to communicate over
        """
        # Step 1: Send our hello message
        # This must happen immediately upon connection before any RPCs
        hello_message = self._build_hello_message()
        self._send_message(channel, hello_message)
        logger.info("Sent NETCONF hello message to client")

        # Step 2: Receive client's hello
        # We don't actually parse it in this minimal implementation,
        # but a production simulator would validate the client's capabilities
        client_hello = self._receive_message(channel)
        if client_hello:
            logger.info("Received client hello message")
        else:
            logger.error("Failed to receive client hello")
            return

        # Step 3: Enter the RPC processing loop
        # Keep receiving and responding to RPCs until the session closes
        while True:
            rpc_request = self._receive_message(channel)

            if not rpc_request:
                # Connection closed or error
                logger.info("Connection closed by client")
                break

            # Parse what the client is asking us to do and generate a response
            rpc_response = self._process_rpc(rpc_request)

            # Send the response back
            self._send_message(channel, rpc_response)

    def _build_hello_message(self):
        """
        Construct the NETCONF hello message.

        The hello message advertises what capabilities this device supports.
        Capabilities are YANG models and protocol features. The client uses
        this to know what operations it can perform on this device.

        Returns:
            XML string containing the hello message
        """
        # This XML structure is defined by RFC 6241
        # The capabilities list tells the client what we support
        hello = '''<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
        <capability>urn:ietf:params:netconf:base:1.0</capability>
        <capability>urn:ietf:params:netconf:base:1.1</capability>
        <capability>urn:ietf:params:netconf:capability:writable-running:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:confirmed-commit:1.0</capability>
        <capability>urn:ietf:params:xml:ns:yang:ietf-interfaces?module=ietf-interfaces&amp;revision=2014-05-08</capability>
        <capability>urn:ietf:params:xml:ns:yang:ietf-ip?module=ietf-ip&amp;revision=2014-06-16</capability>
    </capabilities>
    <session-id>42</session-id>
</hello>]]>]]>'''

        return hello

    def _send_message(self, channel, message):
        """
        Send a NETCONF message over the channel.

        Args:
            channel: The SSH channel to send over
            message: The message string to send (must already include delimiter)
        """
        try:
            channel.send(message.encode('utf-8'))
            logger.debug(f"Sent message: {message[:100]}...")  # Log first 100 chars
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def _receive_message(self, channel):
        """
        Receive a complete NETCONF message from the channel.

        NETCONF 1.0 messages are delimited by ]]>]]> so we read until we see that.

        Args:
            channel: The SSH channel to receive from

        Returns:
            The complete message as a string, or None if connection closed
        """
        message_buffer = ""

        try:
            # Read data in chunks until we see the message delimiter
            while True:
                # recv() blocks until data arrives or connection closes
                chunk = channel.recv(4096).decode('utf-8')

                if not chunk:
                    # Empty chunk means connection closed
                    return None

                message_buffer += chunk

                # Check if we've received a complete message
                if ']]>]]>' in message_buffer:
                    # Extract just the message, not the delimiter
                    message = message_buffer.split(']]>]]>')[0]
                    logger.debug(f"Received message: {message[:100]}...")
                    return message

        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None

    def _process_rpc(self, rpc_request):
        """
        Process an RPC request and generate the appropriate response.

        This examines the RPC XML to determine what operation is being requested,
        then generates a response. We support:
        - get-config: Return current configuration
        - edit-config: Apply configuration changes
        - commit: Commit changes (we just ack)
        - close-session: Gracefully terminate

        Args:
            rpc_request: The RPC request XML string

        Returns:
            The RPC response XML string
        """
        # Simple string matching to determine the operation
        # A production implementation would use proper XML parsing

        if '<get-config>' in rpc_request:
            return self._handle_get_config(rpc_request)

        elif '<edit-config>' in rpc_request:
            return self._handle_edit_config(rpc_request)

        elif '<commit' in rpc_request or '<commit/>' in rpc_request:
            return self._handle_commit(rpc_request)

        elif '<close-session' in rpc_request:
            return self._handle_close_session(rpc_request)

        else:
            # For any operation we don't recognize, return a generic success
            # This keeps the client from breaking on operations we haven't implemented
            return self._build_ok_response(rpc_request)

    def _handle_get_config(self, rpc_request):
        """
        Handle a get-config RPC request.

        The client is asking for current configuration. We return our stored
        device configuration as XML formatted according to YANG models.

        Args:
            rpc_request: The RPC request XML

        Returns:
            RPC response containing configuration data
        """
        # Extract message-id from request so our response can reference it
        # This is required by the NETCONF protocol
        message_id = self._extract_message_id(rpc_request)

        # Build XML showing our current interfaces configuration
        # This uses the ietf-interfaces YANG model structure
        interfaces_xml = ""
        for if_name, if_config in self.device_config['interfaces'].items():
            interfaces_xml += f'''
            <interface>
                <name>{if_name}</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>true</enabled>'''

            # Add IP configuration if it exists
            if 'ipv4' in if_config:
                interfaces_xml += f'''
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>{if_config['ipv4']['ip']}</ip>
                        <netmask>{if_config['ipv4']['netmask']}</netmask>
                    </address>
                </ipv4>'''

            interfaces_xml += '''
            </interface>'''

        # Wrap the interface data in the proper RPC response structure
        response = f'''<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply message-id="{message_id}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            {interfaces_xml}
        </interfaces>
    </data>
</rpc-reply>]]>]]>'''

        logger.info(f"Returning configuration with {len(self.device_config['interfaces'])} interfaces")
        return response

    def _handle_edit_config(self, rpc_request):
        """
        Handle an edit-config RPC request.

        The client is pushing configuration changes. We parse the XML,
        extract the configuration parameters, and update our stored state.

        Args:
            rpc_request: The RPC request XML

        Returns:
            RPC response indicating success or failure
        """
        message_id = self._extract_message_id(rpc_request)

        try:
            # Extract interface configuration from the XML
            # In a production system you'd use a proper XML parser
            # For now, simple string extraction works fine

            if '<name>' in rpc_request:
                # Extract interface name
                if_name = rpc_request.split('<name>')[1].split('</name>')[0]

                # Initialize this interface in our config if it doesn't exist
                if if_name not in self.device_config['interfaces']:
                    self.device_config['interfaces'][if_name] = {}

                # Extract IP address if present
                if '<ip>' in rpc_request:
                    ip_addr = rpc_request.split('<ip>')[1].split('</ip>')[0]
                    netmask = rpc_request.split('<netmask>')[1].split('</netmask>')[0]

                    # Store the IP configuration
                    self.device_config['interfaces'][if_name]['ipv4'] = {
                        'ip': ip_addr,
                        'netmask': netmask
                    }

                    logger.info(f"Configured interface {if_name} with IP {ip_addr}/{netmask}")

            # Return success response
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply message-id="{message_id}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <ok/>
</rpc-reply>]]>]]>'''

        except Exception as e:
            # If parsing fails, return an error response
            logger.error(f"Error processing edit-config: {e}")
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply message-id="{message_id}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <rpc-error>
        <error-type>application</error-type>
        <error-tag>operation-failed</error-tag>
        <error-severity>error</error-severity>
        <error-message>Failed to process configuration</error-message>
    </rpc-error>
</rpc-reply>]]>]]>'''

    def _handle_commit(self, rpc_request):
        """
        Handle a commit RPC request.

        In a real device, commit makes candidate configuration active.
        Our simulator doesn't use separate datastores, so we just acknowledge.

        Args:
            rpc_request: The RPC request XML

        Returns:
            RPC response indicating success
        """
        message_id = self._extract_message_id(rpc_request)
        logger.info("Commit requested - acknowledging")
        return self._build_ok_response_with_id(message_id)

    def _handle_close_session(self, rpc_request):
        """
        Handle a close-session RPC request.

        The client is gracefully terminating the session.

        Args:
            rpc_request: The RPC request XML

        Returns:
            RPC response acknowledging session closure
        """
        message_id = self._extract_message_id(rpc_request)
        logger.info("Session close requested")
        return self._build_ok_response_with_id(message_id)

    def _extract_message_id(self, rpc_request):
        """
        Extract the message-id attribute from an RPC request.

        Every RPC has a message-id that the response must echo back.
        This allows clients to match responses to requests.

        Args:
            rpc_request: The RPC XML string

        Returns:
            The message ID as a string, or "1" if not found
        """
        try:
            # Look for message-id="X" pattern
            start = rpc_request.find('message-id="') + len('message-id="')
            end = rpc_request.find('"', start)
            return rpc_request[start:end]
        except:
            # If we can't find it, use a default
            return "1"

    def _build_ok_response_with_id(self, message_id):
        """
        Build a simple OK response for RPCs that don't return data.

        Args:
            message_id: The message ID to echo in the response

        Returns:
            RPC response XML indicating success
        """
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply message-id="{message_id}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <ok/>
</rpc-reply>]]>]]>'''

    def _build_ok_response(self, rpc_request):
        """
        Build a simple OK response for RPCs that don't return data.

        Extracts the message ID from the request and builds an OK response.

        Args:
            rpc_request: The RPC request XML string

        Returns:
            RPC response XML indicating success
        """
        message_id = self._extract_message_id(rpc_request)
        return self._build_ok_response_with_id(message_id)


class NetconfSSHServer(paramiko.ServerInterface):
    """
    Handles SSH server operations like authentication.
    
    Paramiko calls methods on this class during the SSH handshake to determine
    whether to allow connections and what authentication methods to accept.
    """
    
    def check_auth_password(self, username, password):
        """
        Check if a username/password pair is valid.
        
        For our simulator, we accept any username and password for simplicity.
        In a real device, this would check against a user database.
        
        Args:
            username: The username provided by the client
            password: The password provided by the client
            
        Returns:
            AUTH_SUCCESSFUL if credentials are accepted, AUTH_FAILED otherwise
        """
        # For development, accept any credentials
        # You could add actual credential checking here if needed
        logger.info(f"Authentication attempt - username: {username}")
        return paramiko.AUTH_SUCCESSFUL
    
    def check_channel_request(self, kind, chanid):
        """
        Determine whether to allow a channel request.
        
        Args:
            kind: The type of channel being requested (usually 'session')
            chanid: The channel ID
            
        Returns:
            OPEN_SUCCEEDED to allow the channel, OPEN_FAILED_* otherwise
        """
        # We only support session channels, which is what NETCONF uses
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def get_allowed_auths(self, username):
        """
        Tell the client what authentication methods we support.
        
        Args:
            username: The username (we don't actually use this)
            
        Returns:
            Comma-separated list of allowed auth methods
        """
        # We only support password authentication
        # Real devices might also support public key authentication
        return 'password'
    
    def check_channel_subsystem_request(self, channel, name):
        """
        Handle subsystem requests.
        
        NETCONF runs as an SSH subsystem, specifically the 'netconf' subsystem.
        This method is called when the client requests to start that subsystem.
        
        Args:
            channel: The SSH channel
            name: The subsystem name being requested
            
        Returns:
            True to allow the subsystem, False to deny
        """
        # NETCONF clients request the 'netconf' subsystem
        # This is defined in RFC 6242
        if name == 'netconf':
            logger.info("Client requested NETCONF subsystem - granted")
            return True
        
        logger.warning(f"Client requested unknown subsystem: {name}")
        return False


if __name__ == '__main__':
    """
    Entry point when running the simulator directly.
    
    Creates a simulator instance and starts it listening for connections.
    Runs until interrupted with Ctrl-C.
    """
    print("=" * 60)
    print("NETCONF Device Simulator")
    print("=" * 60)
    print()
    print("This simulator pretends to be a network device supporting NETCONF.")
    print("Your SDN controller can connect to it for development and testing.")
    print()
    print("Press Ctrl-C to stop the simulator")
    print()
    
    simulator = NetconfDeviceSimulator(
        listen_address='127.0.0.1',  # Only accept local connections
        listen_port=8300             # Non-standard port to avoid conflicts
    )
    
    simulator.start()