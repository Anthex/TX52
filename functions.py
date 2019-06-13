from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from operator import itemgetter as ig
import time
import serial
import sys

vectorsPerFP = 3 #number of samples per FP

#Terminal output formatters
class output:
    NORMAL = '\033[39;37;40m'
    RED = '\033[0;31;40m'
    GREEN = '\033[1;32;40m'
    TEAL = '\033[38;5;51m'
    ORANGE = '\033[38;5;229m'
    HIGHLIGHTED = '\033[03;30;47m'
    CLEAR = chr(27)+'[2j\033c\x1bc'
    SLOWBLINK = '\033[5;37;40m'
    
def printf(*argv, end='\n'):
        for arg in argv:
                print(str(arg).format(output=output), end='')
                print(output.NORMAL, end='')
        print(end, end='')
        sys.stdout.flush()

try:
    ser = serial.Serial(
        port = 'COM4',
        baudrate = 9600,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
except Exception  as e:
    printf("{output.RED}error accessing COM port: " + str(e))
    exit()

engine = create_engine('sqlite:///fp.db')
base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class AP(base):
    __tablename__ = "AP"
    ID=Column(Integer, primary_key=True)
    X=Column(Float)
    Y=Column(Float)
    Z=Column(Float)


class RSSVector(base):
    __tablename__ = "Vector"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    RSSI1=Column(Float)
    RSSI2=Column(Float)
    RSSI3=Column(Float)

    def toString(self):
        return ("("+str(self.RSSI1)+","+str(self.RSSI2)+","+str(self.RSSI3)+")") 

class Fingerprint(base):
    __tablename__ = "Fingerprint"
    ID=Column(Integer, primary_key=True)
    Vector_ID = Column(Integer, ForeignKey("Vector.ID"))
    vec = relationship("RSSVector", backref="Fingerprint")
    X=Column(Float)
    Y=Column(Float)
    Z=Column(Float)

    def toString(self):
        return ("("+str(self.X)+","+str(self.Y)+","+str(self.Z)+")") 

class SampleToLocate():
    def __init__(self, r1, r2, r3):
        self.R1 = r1
        self.R2 = r2
        self.R3 = r3

def BeginFingerprinting(coord):
    x,y = coord[0], coord[1]
    fingerprints = []
    printf("{output.NORMAL}listening for vectors on serial port...")
    try:
        ser.flushInput()
        for k in range(0,vectorsPerFP):
            incoming = str(ser.readline())
            fingerprints.append(treat(incoming,k))
    except Exception as e2:
        printf("{output.RED}Error : " + str(e2))

    finalRSSI = RSSVector(RSSI1=0, RSSI2=0, RSSI3=0)
    for fp in fingerprints:
        finalRSSI.RSSI1 += fp.RSSI1
        finalRSSI.RSSI2 += fp.RSSI2
        finalRSSI.RSSI3 += fp.RSSI3
    finalRSSI.RSSI1 /= len(fingerprints)
    finalRSSI.RSSI2 /= len(fingerprints)
    finalRSSI.RSSI3 /= len(fingerprints)
    session.add(finalRSSI)
    session.commit()
    fp = Fingerprint(Vector_ID=finalRSSI.ID, X=x, Y=y, Z=0)
    session.add(fp)
    session.commit()
    printf("{output.GREEN}Fingerprint successfully added{output.NORMAL}, Coordinates : " + str(fp.toString()) + " - ID : " + str(fp.ID) + " - RSSI : " + fp.vec.toString() + "\r\n\r\n")

def defineAPs():
    AP1 = AP(ID=1, X=3.4, Y=50.3, Z=43.2)
    AP2 = AP(ID=2, X=9.4, Y=90.3, Z=44.2)
    AP3 = AP(ID=3, X=9.4, Y=90.3, Z=44.2)
    session.add(AP1)
    session.add(AP2)
    session.add(AP3)
    session.commit()

def treat(incoming, seq=0):
    VectorString = incoming.split('(')[1].split(')')[0] #we only get the inside of the parenthesis, ex : 11,22,33
    VectorArgs = VectorString.split(',')
    result = RSSVector(RSSI1=int(VectorArgs[0]), RSSI2=int(VectorArgs[1]), RSSI3=int(VectorArgs[2]))
    printf("{output.GREEN}Vector "+str(seq+1)+"/"+str(vectorsPerFP) + " received : " + result.toString())
    return result

""" returns an array w/ the 4 closest fingerprint points
"""
def findKNeighbours(Sample):
    distances = []
    for fp in session.query(Fingerprint).all():
        dist = abs(Sample.R1 - fp.vec.RSSI1) \
            + abs(Sample.R1 - fp.vec.RSSI2) \
            + abs(Sample.R1 - fp.vec.RSSI3) 
        distances.append((dist, fp))
    distances = sorted(distances, key=ig(0))
    return [x[1] for x in distances][:4]
