from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from operator import itemgetter as ig
import subprocess
import serial
import model
import math
import time
import sys
import os

vectorsPerFP = 3 #number of samples per FP
DBNAME='fp.db'


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

def beginSerial(portName, br=9600):
    try:
        ser = serial.Serial(
            port = portName,
            baudrate = br,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
    except Exception as e:
        printf("{output.RED}error accessing COM port: " + str(e))
        exit(1)
    return ser

""" feeds sql scheme to sqlite3
    alternatively, you can just use "cat schema.sql | sqlite3"
"""
def resetDB(backupOld=True):
    if backupOld:
        if os.path.isfile('{}'.format(DBNAME)):
            if subprocess.call("cp {} {}.old".format(DBNAME, DBNAME)):
                printf("{output.RED}error: COULD NOT BACKUP DATABASE")
                return False
            if subprocess.call("rm {}".format(DBNAME)):
                printf("{output.RED}error: COULD NOT DELETE PREVIOUS DATABASE")
                return False
    if os.path.isfile('schema.sql'):
        os.system("cat schema.sql | sqlite3")
    else:
        printf("{output.RED}error: NO SQL SCHEMA FOUND")
        return False
    if not os.path.isfile('{}'.format(DBNAME)):
        printf("{output.RED}error: DATABASE NOT CREATED")
        return False
    printf("{output.GREEN}DATABASE RESET SUCCESSFULLY")
    return True



engine = create_engine('sqlite:///'+DBNAME)
base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class AP(base):
    __tablename__ = "AP"
    ID=Column(Integer, primary_key=True)
    X=Column(Float)
    Y=Column(Float)
    Z=Column(Float)

    def distanceTo(self, sample):
        return math.sqrt(pow(self.X - sample[0], 2) + pow(self.Y - sample[1], 2) + pow(self.Z - sample[2],2))

class RSSVector(base):
    __tablename__ = "Vector"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    RSSI1=Column(Float)
    RSSI2=Column(Float)
    RSSI3=Column(Float)

    def toString(self):
        return ("("+str(round(self.RSSI1,1))+","+str(round(self.RSSI2,1))+","+str(round(self.RSSI2,1))+")") 

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

    def distanceTo(self, loc):
        return math.sqrt(pow(self.X - loc.X, 2) + pow(self.Y - loc.Y, 2) + pow(self.Z - loc.Z,2))
        
class SampleToLocate():
    def __init__(self, r1, r2, r3):
        self.R1 = r1
        self.R2 = r2
        self.R3 = r3

    def Sadowski(self):
        coord = []
        coord.append(model.Sadowski_D_FROM_RSSI(self.R1))
        coord.append(model.Sadowski_D_FROM_RSSI(self.R2))
        coord.append(model.Sadowski_D_FROM_RSSI(self.R3))
        return coord #(D1, D2, D3)

    def FriisLike(self):
        coord = []
        coord.append(model.FriisLike(self.R1))
        coord.append(model.FriisLike(self.R2))
        coord.append(model.FriisLike(self.R3))
        return coord #(D1, D2, D3)

    """ returns tuple of arrays w/ the 4 closest fingerprint points
        (distances[], fingerprints[])
    """
    def findKNeighbours(self):
        distances = []
        for fp in session.query(Fingerprint).all():
            dist = abs(self.R1 - fp.vec.RSSI1) \
                 + abs(self.R1 - fp.vec.RSSI2) \
                 + abs(self.R1 - fp.vec.RSSI3)
            distances.append((dist, fp))
        distances = sorted(distances, key=ig(0))
        return [x[0] for x in distances][:4], [x[1] for x in distances][:4]

    """ returns an array containing [X,Y,Z] of the estimated location, ugly AF -> to refactor eventually
    """
    def resolve_barycenter(self):
        d, nC = self.findKNeighbours()
        return \
          [ 1 / (1+d[0]/d[1]+d[0]/d[2]+d[0]/d[3])*nC[0].X + 1 / (1+d[1]/d[0]+d[1]/d[2]+d[1]/d[3])*nC[1].X + 1 / (1+d[2]/d[1]+d[2]/d[0]+d[2]/d[3])*nC[2].X + 1 / (1+d[3]/d[1]+d[3]/d[2]+d[3]/d[0])*nC[3].X, 
          1 / (1+d[0]/d[1]+d[0]/d[2]+d[0]/d[3])*nC[0].Y + 1 / (1+d[1]/d[0]+d[1]/d[2]+d[1]/d[3])*nC[1].Y + 1 / (1+d[2]/d[1]+d[2]/d[0]+d[2]/d[3])*nC[2].Y + 1 / (1+d[3]/d[1]+d[3]/d[2]+d[3]/d[0])*nC[3].Y, 
          1 / (1+d[0]/d[1]+d[0]/d[2]+d[0]/d[3])*nC[0].Z + 1 / (1+d[1]/d[0]+d[1]/d[2]+d[1]/d[3])*nC[1].Z + 1 / (1+d[2]/d[1]+d[2]/d[0]+d[2]/d[3])*nC[2].Z + 1 / (1+d[3]/d[1]+d[3]/d[2]+d[3]/d[0])*nC[3].Z ]

def BeginFingerprinting(ser, coord):
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
        exit(1)

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


