import logging
logger = logging.getLogger(__name__)
import socket
import time
import atexit

import logging
import socket
import time

# Create a logger instance
logger = logging.getLogger(__name__)

#TODO: Needs to be tested more thoroughly
class TCPClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None
        self.connected = False
        self.last_data = None
        
        atexit.register(self.close)

    def connect(self):
        """Connect to the server."""
        while not self.connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.server_ip, self.server_port))
                self.connected = True
                logger.info(f"Connected to {self.server_ip}:{self.server_port}.")
            except ConnectionRefusedError:
                logger.error(f"Connection with {self.server_ip}:{self.server_port} refused. Retrying in 5 seconds...")
                time.sleep(5)
                continue
            except OSError as e:
                logger.error(f"Error connecting to {self.server_ip}:{self.server_port}. Retrying in 5 seconds...")
                logger.error(e)
                time.sleep(5)
                continue

    def send_data(self, data):
        """Send data to the server."""
        
        attempts = 0
        
        if not self.connected:
            logger.error(f"Not connected to server. Call connect() method first.")
            return
        
        try:
            self.sock.sendall(data.encode())
        except BrokenPipeError:
            logger.error("Connection lost. Retrying...")
            self.connected = False
            self.connect()
            
            # Wait for 5 seconds before retrying
            time.sleep(5)
            if attempts < 2:
                self.send_data(data)
                logger.info(data)

    #TODO: Set timeout and treat it as an error
    def receive_data(self, conn = 'serial'):
        """Receive data from the server."""
        if not self.connected:
            logger.error("Not connected to server. Call connect() method first.")
            return
        
        try:
            data = ''
            if conn == 'io':
                while True:
                    data = self.sock.recv(16)
                    if not data:
                        break
                    return data
            
            else:  
                while True:
                    chunk = self.sock.recv(64)
                    if not chunk or chunk.decode('utf-8', errors='ignore')[-1] in ('>', '?'):
                        data += chunk.decode('utf-8', errors='ignore')
                        break
                    else:
                        data += chunk.decode('utf-8', errors='ignore')
                return data

        except ConnectionResetError:
            logger.error("Connection lost. Retrying...")
            self.connected = False
            self.connect()
            return self.receive_data('utf-8', errors='ignore')

        except Exception as e:
            logger.debug("Error receiving data.")
            logger.debug(e)
            return

    def close(self):
        """Close the TCP connection."""
        if self.connected:
            self.sock.close()
            self.connected = False
            print("Connection closed.")

    def reconnect(self):
        """Reconnect to the server."""
        self.close()
        self.connect()

    def clean_socket_buffer(self):
        """
        Clean the buffer of a TCP socket.

        Args:
            sock (socket.socket): The TCP socket object.

        Returns:
            None
        """
        # Set a timeout on the socket
        self.sock.settimeout(1)  # Set the timeout period as needed

        try:
            while True:
                # Attempt to receive data from the socket
                data = self.sock.recv(4096)  # Adjust the buffer size as needed

                # If no data is received, break out of the loop
                if not data:
                    break

        except socket.timeout:
            # Timeout occurred, indicating that the buffer is empty
            pass

        finally:
            # Reset the timeout on the socket to None
            self.sock.settimeout(None)
