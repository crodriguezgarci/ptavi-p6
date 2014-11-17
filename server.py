#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""
import sys
import SocketServer
import os.path
import os

METODOS_PERMITIDOS = ["INVITE","BYE","ACK"]

#Datos de conexión

if not os.path.exists(sys.argv[3]) or len(sys.argv) != 4:
    print "Usage: python server.py IP port audio_file"
    sys.exit()


SERVER = sys.argv[1]
PORT_SIP = int(sys.argv[2])
AUDIO = sys.argv[3]

PORT_RTP = 23032
SERVER_RTP = "127.0.0.1"
COMANDO = './mp32rtp -i ' + SERVER_RTP + ' -p ' + str(PORT_RTP)  + ' < ' + AUDIO

class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            if line != "":
                if "\r\n\r\n" in line:
                    print "El cliente nos manda " + line
                    line = line.split()
                    if ('sip:' in line[1][:4]) and (line[2] == "SIP/2.0") and ('@' in line[1]):
                        if line[0] == "INVITE":
                            self.wfile.write("SIP/2.0 100 Trying\r\n\r\n")
                            self.wfile.write("SIP/2.0 180 Ring\r\n\r\n")
                            self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                        elif line[0] == "ACK":
                            print "Comienza el RTP " + COMANDO
                            os.system(COMANDO)
                            print "La canción ha terminado"
                        elif line[0] == "BYE":
                            self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                        elif line[0] not in METODOS_PERMITIDOS:
                            self.wfile.write("SIP/2.0 405 Method Not Allowed\r\n")
                    else:
                        self.wfile.write("SIP/2.0 400 Bad Request\r\n")
                else:
                    self.wfile.write("SIP/2.0 400 Bad Request\r\n")
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = SocketServer.UDPServer(("", PORT_SIP), EchoHandler)
    print "Listening..."
    serv.serve_forever()
