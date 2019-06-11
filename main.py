from functions import *
from gui import *

def main():
    if not len(session.query(AP).all()):
        printf("APs non definis, ajout")
        defineAPs()

    printf("beginning")
    try: 
        ser.close()
        printf("opening port...")
        ser.open()
    except Exception  as e:
        printf("{output.RED}error open serial port: " + str(e))
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
                printf("{output.TEAL}Press Enter to add new fingerprint...")
                input()
                coord = selectPosition()
                printf("{output.ORANGE}Confirm position : {output.GREEN}" + str(coord[0]) + " , " + str(coord[1]) + "{output.ORANGE} ? (Enter to confirm, any key to cancel)")
                
                if input():
                    coord = []
                if coord:
                    BeginFingerprinting(coord)
        except Exception as e1:
            printf("{output.RED}error : " + str(e1))
    else:
        printf("{output.RED}port wasn't open")
    ser.close()


main()
