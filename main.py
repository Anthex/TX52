from functions import *
from gui import *

def main():
    if not len(session.query(AP).all()):
        printf("{output.ORANGE}Info : APs non definis, ajout des AP par defaut (definis dans functions.py)")
        defineAPs()

    printf("beginning")
    try: 
        ser.close()
        printf("opening port...")
        ser.open()
    except Exception  as e:
        printf("{output.RED}error opening serial port: " + str(e))
        exit()

    if ser.isOpen():
        try:
            printf("port open")
            ser.flushInput()
            ser.flushOutput()
            while(1):
                # WAIT FOR USER INPUT (ID)
                """
                printf("Input X\r\n{output.TEAL}>> ", end='')
                coord.append(input())
                printf("Input Y\r\n{output.TEAL}>> ", end='')
                coord.append(input())
                """
                """ WAIT FOR USER INPUT
                printf("{output.TEAL}Press Enter to add new fingerprint...")
                input()
                """
                coord = selectPosition(session.query(Fingerprint).all())
                printf("{output.NORMAL}Begin sampling at location : {output.GREEN}" + str(coord[0]) + " , " + str(coord[1]))
                
                """
                printf("{output.ORANGE}Confirm position : {output.GREEN}" + str(coord[0]) + " , " + str(coord[1]) + "{output.ORANGE} ? (Enter to confirm, any key to cancel)")
                if input():
                    coord = []
                """
                if coord:
                    BeginFingerprinting(coord)
        except Exception as e1:
            printf("{output.ORANGE}\r\nThank you for playing Wing Commander ! ")
    else:
        printf("{output.RED}port wasn't open")
    ser.close()


main()
