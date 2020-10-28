import socket
import struct
import sys
import hashlib
from datetime import datetime
import time

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

message = "Mensaje en multidifusion"
multicast_group = ("224.3.29.71", 10000)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.settimeout(0.2)

ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:
    logFile = open(datetime.now().strftime("%d%m%Y%H%M%S")+".txt", "a")
    logFile.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    sent = sock.sendto(message.encode("ascii"), multicast_group)
    while True:
        try:
            #Recibe 0 o 1 dependiendo del archivo
            data, server = sock.recvfrom(16)
            print("Archivo:", data)
            logFile.write("\nLOG:Archivo:"+str(data))
            if(data == b'0'):
                fileToSend = open('text1.txt', 'rb')
                sock.sendto(fileToSend.name.encode("ascii"), multicast_group)
                i = 0
                info = fileToSend.read(1024*30)
                while info:
                    #print("Enviado de", i, "KB a", i + 30, "KB")
                    logFile.write("\nLOG:Enviado de " + str(i) +" KB a "+ str(i + 30) + " KB")
                    if i ==0:
                        start = str(time.time()).encode("ascii")
                        sock.sendto(start, multicast_group)
                    i += 30
                    sock.sendto(info, multicast_group)
                    info = fileToSend.read(1024*30)
                    #Recibe el ACK
                    print("Recibido", data, "de", server)
                    logFile.write("\nLOG:Recibido " + str(data) + " de " + str(server))
                    data, server = sock.recvfrom(16)
                message = "end"
                logFile.write("\nLOG:FINALIZO EL ENVIO")
                sock.sendto(message.encode("ascii"), multicast_group)
            else:
                fileToSend = open('text2.txt', 'rb')
                sock.sendto(fileToSend.name.encode("ascii"), multicast_group)
                i = 0
                info = fileToSend.read(1024*30)
                while info:
                    #print("Enviado de", i, "KB a", i + 30, "KB")
                    logFile.write("\nLOG:Enviado de " + str(i) +" KB a "+ str(i + 30) + " KB")
                    if i ==0:
                        start = time.time()
                        sock.sendto(start, multicast_group)
                    i += 30
                    sock.sendto(info, multicast_group)
                    info = fileToSend.read(1024*30)
                    #Recibe el ACK
                    print("Recibido", data, "de", server)
                    logFile.write("\nLOG:Recibido " + str(data) + " de " + str(server))
                    data, server = sock.recvfrom(16)
                message = "end"
                logFile.write("\nLOG:FINALIZO EL ENVIO")
                sock.sendto(message.encode("ascii"), multicast_group)
            #Recibe el ACK
            data, server = sock.recvfrom(16)
        except socket.timeout:
            print("Timeout cumplido. No se recibio respuesta")
            logFile.write("\nLOG:Timeout cumplido. No se recibio respuesta")
            break
        else:
            print("Recibido", data, "de", server)
            logFile.write("\nLOG:Recibido" + str(data) + " de " + str(server))
finally:
    hashCode = getsha256file(fileToSend.name)
    sock.sendto(hashCode.encode("ascii"), multicast_group)
    print("Codigo Hash del servidor", hashCode)
    logFile.write("\nLOG:Codigo Hash del servidor "+str(hashCode))
    print("Socket cerrado")
    logFile.write("\nLOG:Socket cerrado")
    logFile.close()
    sock.close()