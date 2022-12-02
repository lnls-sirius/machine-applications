
# Run this at ioc side to emulate serial port, and get the name of virtual serial port created.
socat -d -d pty,raw,echo=0 tcp:10.1.2.156:9993
socat -d -d pty,raw,echo=0 tcp:10.1.2.156:9993