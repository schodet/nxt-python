import nxt.locator
from nxt.motor import *
from nxt.sensor import *
import socket, thread

def SENDRESULT(csock,ip,result):
        try:
            csock.send(result)
        except:
            print 'connection to '+ip+' terminated. unable to send command result code.'

def SERVECLIENT(csock,info,ip):
    exitcode = 0
    
    try:
        csock.send('0')
    except:
        print 'connection to '+ip+' terminated. unable to send connection success code.'
        csock.close()
        thread.exit_thread()

    while exitcode = 0:
        try:
            cmd = csock.recv(100)
        except:
            print 'connection to '+ip+' terminated. unable to recieve command data.'
            exitcode = 1
        if cmd == 'find_brick':
            try:
                b = nxt.locator.find_one_brick()
                b.connect()
            except:
        elif cmd == 'close_brick':
            try:
                b.close()
                try:
                    csock.send('0')
                except:
                    print 'connection to '+ip+' terminated. unable to send command success code.'
            except:
                try:
                    csock.send('1')
                except:
                    print 'connection to '+ip+' terminated. unable to send command failure code.'
            

def NEWCLIENTS(sock):
    while 1:
        client, info = sock.accept()
        print 'new client with info: ' + info
        thread.start_new_thread(SERVECLIENT,(client,info,info[0]))

def serve_forever():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 54174))
    sock.listen(5)
    thread.start_new_thread(NEWCLIENTS, (sock,))
