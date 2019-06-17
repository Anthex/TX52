from functions import *
from gui import *
import serial.tools.list_ports
import getopt 

class method:
    GRAPHICAL = 0
    MANUAL = 1 # /!\ Manual method does not validate input, using waitForUserConfirmation = True is recommended

inputMethod = method.GRAPHICAL
waitForUserValidation = False
waitForUserConfirmation = False
serialPort = "COM11"

def main():
    ser = beginSerial(serialPort)

    if not len(session.query(AP).all()):
        printf("{output.ORANGE}Info : APs not defined, adding default APs (defined in functions.py)")
        defineAPs()

    printf("beginning")
    try: 
        ser.close()
        printf("opening port...")
        ser.open()
    except Exception  as e:
        printf("{output.RED}error opening serial port: " + str(e))
        exit(1)

    if ser.isOpen():
        try:
            printf("{output.GREEN}port open")
            ser.flushInput()
            ser.flushOutput()
            while(1):
                coord = [] #X,Y of the Fingerprint to add
                # WAIT FOR USER INPUT (ID)
                if inputMethod == method.MANUAL:
                    printf("Input X\r\n{output.TEAL}>> ", end='')
                    coord.append(input())
                    printf("Input Y\r\n{output.TEAL}>> ", end='')
                    coord.append(input())
                else:
                    if waitForUserValidation:
                        printf("{output.TEAL}Press Enter to add new fingerprint...")
                        input()
                    
                    coord = selectPosition(session.query(Fingerprint).all())
                    printf("{output.NORMAL}Begin sampling at location : {output.GREEN}" + str(coord[0]) + " , " + str(coord[1]))
                
                if waitForUserConfirmation:
                    printf("{output.ORANGE}Confirm position : {output.GREEN}" + str(coord[0]) + " , " + str(coord[1]) + "{output.ORANGE} ? (Enter to confirm, any key to cancel)")
                    if input():
                        coord = []
                if coord:
                    BeginFingerprinting(ser, coord)

        except Exception as _:
            printf("{output.ORANGE}\r\nThank you for playing Wing Commander ! ")
    else:
        printf("{output.RED}port wasn't open")
    ser.close()

def locateSampleOnSerial():
    ser = beginSerial(serialPort)
    printf("{output.NORMAL}listening for vectors on serial port...")
    try:
        ser.flushInput()
        incoming = str(ser.readline())
        vector = treat(incoming)
    except Exception as e2:
        printf("{output.RED}Error : " + str(e2))
        exit(1)
    sample = SampleToLocate(vector.RSSI1, vector.RSSI2, vector.RSSI3)
    printf(sample.resolve_barycenter())
    showLocation(session.query(Fingerprint).all(), sample.findKNeighbours()[1], sample.resolve_barycenter())
    exit()                

if __name__ == "__main__": 
    try:
        opts, args = getopt.getopt(sys.argv[1:],  'c', ['method=', 'reset', 'port=', 'locate=','db=','nsamples='])
        for opt, value in opts:
            if opt == '-c':
                waitForUserConfirmation = True
                waitForUserValidation = True
            elif opt == '--reset':
                printf("{output.ORANGE} You are about to reset the database, continue? (Y/N)")
                resp = input()
                if resp == 'y' or resp =='Y':
                    resetDB()
            elif opt == '--method':
                if value == 'graphical':
                    inputMethod = method.GRAPHICAL
                    printf("{output.ORANGE}Input method overridden to GRAPHICAL")
                elif value == 'manual':
                    inputMethod = method.MANUAL
                    waitForUserConfirmation = True
                    printf("{output.ORANGE}Input method overridden to MANUAL")
                else:
                    printf("{output.RED} Wrong value for method, expected either 'graphical' or 'manual'")
                    exit(1)
            elif opt == '--port':
                if value:
                    serialPort = value
                    if value == "auto":
                        ports = serial.tools.list_ports.comports(include_links=False)
                        if ports:
                            serialPort = ports[0].device
                            printf("{output.GREEN}Automatically selected port " + serialPort)
                        else:
                            printf("{output.RED}Error : No serial ports found ")
                            exit(1)
                else:
                    printf("{output.RED}Please specify a serial port (e.g. --port=COM5)")
                    exit(1)
            elif opt == '--locate':
                if value == 'serial':
                    locateSampleOnSerial()
                else:
                    r1,r2,r3=map(int,value.split(','))
                    sample = SampleToLocate(r1,r2,r3)
                    printf(sample.resolve_barycenter())
                    printf(sample.Sadowski())
                    printf(sample.FriisLike())
                    showLocation(session.query(Fingerprint).all(), sample.findKNeighbours()[1], sample.resolve_barycenter())
                    exit()
            elif opt == '--db':
                DBNAME=value #rework db init for this to work
            elif opt =='--nsamples':
                if value:
                    vectorsPerFP = int(value)
                else:
                    printf("{output.RED}No value specified for nsamples")
                    exit(1)
    except getopt.error as _:
            printf("{output.RED}Wrong parameters. {output.NORMAL}\r\nUsage : \r\n --reset : resets/creates the FP database \r\n --method=(graphical/manual) : sets input type\r\n --port=<name> : listens on specified port\r\n\
 --locate=r1,r2,r3 or --locate=serial : graphically locates the sample with (r1,r2,r3)\r\n --db=dbname.db : use specified database\r\n --nsamples=n : set #of samples per FP \r\n -c : force user validation")
            exit(1)
    main()

