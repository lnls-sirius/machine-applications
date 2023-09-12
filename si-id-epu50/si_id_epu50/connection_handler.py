"""Connection handler module."""

import socket
import time
import atexit
import logging

# Create a logger instance
logger = logging.getLogger(__name__)


class TCPClient:
    """TCP client."""

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
                self.sock.settimeout(5)
                self.sock.connect((self.server_ip, self.server_port))
                self.connected = True
                logger.info("Connected to %s:%s.", self.server_ip, self.server_port)
            except ConnectionRefusedError:
                logger.error(
                    "Connection with %s:%s \
                        refused. Retrying in 5 seconds...",
                    self.server_ip,
                    self.server_port,
                )
                time.sleep(5)
                continue
            except OSError as e:
                logger.error(
                    "Error connecting to %s:%s. \
                        Retrying in 5 seconds...",
                    self.server_ip,
                    self.server_port,
                )
                logger.error(e)
                time.sleep(5)
                continue

    def send_data(self, data):
        """Send data to the server."""

        attempts = 0

        if not self.connected:
            logger.error("Not connected to server. Call connect() method first.")
            return

        try:
            self.sock.sendall(data.encode())
        except BrokenPipeError:
            logger.exception("Connection lost. Retrying...")
            self.connected = False
            self.connect()

            # Wait for 5 seconds before retrying
            time.sleep(5)
            if attempts < 2:
                self.send_data(data)
                logger.info(data)

    # TODO: Set timeout and treat it as an error
    def receive_data(self, conn="serial"):
        """Receive data from the server."""
        if not self.connected:
            logger.error("Not connected to server. Call connect() method first.")
            return

        try:
            data = ""
            if conn == "io":
                while True:
                    data = self.sock.recv(16)
                    if not data:
                        break
                    return data

            else:
                while True:
                    chunk = self.sock.recv(64)

                    if not chunk:
                        break

                    chunk_str = chunk.decode("utf-8", errors="ignore")
                    if chunk_str[-1] in (">", "?"):
                        data += chunk_str
                        break

                    else:
                        data += chunk_str

                return data

        except ConnectionResetError:
            logger.error("Connection lost. Retrying...")
            self.connected = False
            self.connect()
            return self.receive_data("utf-8")

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
        self.sock.settimeout(2)

        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    break

        except socket.timeout:
            pass

        finally:
            self.sock.settimeout(None)
