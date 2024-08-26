
import driver
import pcaspy
import pvs

PREFIX = 'SIPA-'
INTERVAL = 0.1


def run():
    """."""
    server = pcaspy.SimpleServer()
    server.createPV(PREFIX, pvs.pvdb)
    pcas_driver = driver.PCASDriver()
    _ = pcas_driver

    while True:
        server.process(INTERVAL)
