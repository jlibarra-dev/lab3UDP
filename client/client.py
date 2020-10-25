import socket
import struct
import sys
import hashlib
from datetime import datetime

def getsha256file(archivo):
    try:
        hashsha = hashlib.sha256()
        with open(archivo, "rb") as f:
            for bloque in iter(lambda: f.read(4096), b""):
                hashsha.update(bloque)
        return hashsha.hexdigest()
    except Exception as e:
        print("Error: %s" % (e))
        return ""
    except:
        print("Error desconocido")
        return ""

ack = 'ack'
multicast_group = "224.3.29.71"
server_adress = ('', 10000)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

sock.bind(server_adress)

group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
archivo = input("Seleccion 0 para el archivo de 100 MB y seleccion 1 para el archivo de 250 MB: ")

logFile = open(datetime.now().strftime("%d%m%Y%H%M%S")+".txt", "a")
while True:
    print("\nEsperando para recibir mensaje")
    logFile.write("\nLOG:Esperando para recibir mensaje")
    data, address = sock.recvfrom(1024)

    print("Recibio", len(data), "bytes de", address)
    print(data)
    logFile.write("\nLOG:Recibio " + str(len(data)) + " bytes de" + str(address))
    
    print("Enviado archivo deseado a",address)
    sock.sendto(archivo.encode("ascii"), address)
    logFile.write("\nLOG:Enviado archivo deseado a"+str(address))
    
    #Recibe el nombre del archivo
    data, address = sock.recvfrom(1024)
    nombreArchivo = data.decode("ascii")
    logFile.write("\nLOG:Archivo"+str(nombreArchivo))

    print("Recibio", len(data), "bytes de", address)
    print(data)
    logFile.write("\nLOG:Recibio "+str(len(data))+" bytes de"+str(address))
    
    newFile = open(nombreArchivo,"w")
    i = 0
    while True:
        data, address = sock.recvfrom(1024*30)
        if(data == b'end'):
            break
        logFile.write("\nLOG:Recibio de "+str(i)+ " KB a " + str(i + 30)+ " KB")
        newFile.write(data.decode("utf-8"))
        print("Enviando ACK a", address, "#", i)
        logFile.write("\nLOG:Enviando ACK a " + str(address)+" #"+str(i))
        i+=1
        sock.sendto(ack.encode("ascii"), address)
    newFile.close()  
    hashCode = getsha256file(nombreArchivo)
    print(hashCode)
    logFile.write("\nLOG:HascCode local: " + hashCode)
    data, address = sock.recvfrom(1024)
    hashRcv = data.decode("ascii")
    logFile.write("\nLOG:HascCode del servidor: " + hashRcv)
    if (hashRcv == hashCode):
        print("INTEGRIDAD EXITOSA")
        logFile.write("\nLOG:INTEGRIDAD EXITOSA")
    else:
        print("\nINTEGRIDAD FALLIDAD. REVISAR ENVIO.")
        logFile.write("LOG:INTEGRIDAD FALLIDAD. REVISAR ENVIO.")
    print("Enviando ACK a", address)
    logFile.write("\nLOG:Enviando ACK a " + str(address))
    sock.sendto(ack.encode("ascii"), address)
    logFile.close()
    break
    