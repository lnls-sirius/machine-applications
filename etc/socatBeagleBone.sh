Use this to write messages received by socat on beagle bone to log file:

socat -u TCP4-LISTEN:9993,reuseaddr,fork OPEN:/tmp/test.log,creat,append

socat -ddd file:/dev/ttyUSB0,b19200,echo=0,raw TCP-LISTEN:11313,reuseaddr,fork