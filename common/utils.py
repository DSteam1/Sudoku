import logging
from constants import SERVER_CONFIGURATION_FILE


def init_logging():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
    return logging.getLogger()


def get_server_address_and_port():
    with open(SERVER_CONFIGURATION_FILE, "r") as f:
        contents = f.readlines()
        ip_address = contents[0].strip()
        port = int(contents[1].strip())
    return ip_address, port
