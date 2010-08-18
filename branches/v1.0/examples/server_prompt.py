#This script is an example for the nxt.server module. You need to run
#nxt.server.serve_forever() in another window. Or, if you want to use
#this across a network, pass the IP of the computer running the server
#as an argument in the command line.

import socket, sys

try:
    server = sys.argv[1]
    bindto = ''
except:
    server = 'localhost'
    bindto = 'localhost'

insock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
outsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
insock.bind((bindto, 54374))

while 1:
    command = raw_input('nxt> ')
    outsock.sendto(command, (server, 54174))
    retvals, addr = insock.recvfrom(1024)
    retcode = retvals[0]
    retmsg = retvals[1:len(retvals)]
    print 'Return code: '+retcode
    print 'Return message: '+retmsg
