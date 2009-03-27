#This script is an example for the nxt.server module. You need to run
#nxt.server.serve_forever() in another window.

import socket

insock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
outsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
insock.bind(('localhost', 54374))

while 1:
    command = raw_input('nxt> ')
    outsock.sendto(command, ('localhost', 54174))
    retvals, addr = insock.recvfrom(1024)
    retcode = retvals[0]
    retmsg = retvals[1:retvals.index('~')]
    print 'Return code: '+retcode
    print 'Return message: '+retmsg
