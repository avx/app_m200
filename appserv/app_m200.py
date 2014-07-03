#!/usr/bin/python

M200_IP='10.66.0.200'
M200_DESCR=''
SCOMM_HOST='127.0.0.1'
SCOMM_PORT=10001
SCOMM_INFOPORT=11001
SCOMM_PROTV=10

#MASTER="http://10.66.0.6:8888/status"

import tornado.websocket
import tornado.ioloop
import tornado.web
import functools
import pprint
import socket
import errno
import json
import time
import sys
import os
import re

def log(*args):
        msg='';
        for arg in args:
          msg=msg+str(arg);
        print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),":",msg)

class M200:
        def __init__(self,host='127.0.0.1',port=10001,infoport=11001,protv=11):
          self.SCOMM_HOST=host
          self.SCOMM_PORT=port
          self.SCOMM_INFOPORT=port+1000
          self.SCOMM_PROTV=protv
          self.overload=0
          self.scomm={}
          self.groupinfo={}
          self.pcmstatus={}
          self.scomm_get_info()
          self.connect()
#          self.disconnect()

        def scomm_start(self):
          os.system("/opt/m200/scomm "+M200_IP+" 10000 "+str(self.SCOMM_PORT)+" -infoport "+str(self.SCOMM_INFOPORT)+" -protv "+str(self.SCOMM_PROTV)+" -logfile /opt/m200/log/scomm.log -d > /dev/null 2>&1");
          del self.scomm['Status']
          return 1

        def scomm_stop(self):
          print ("call scomm_stop()")
          if self.scomm:
            if 'Pid' in self.scomm:
               os.system("kill -9 "+m200.scomm['Pid'])
               self.scomm={}
               self.scomm['Status']="stopped"
               return 1
          return 0

        def scomm_get_info(self):
          print("scomm_get_info() start")
          tornado.ioloop.IOLoop.current().add_timeout(time.time() + 5, lambda:self.scomm_get_info())
          try:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.SCOMM_HOST, int(self.SCOMM_INFOPORT)))
          except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
              print ("Couldn't connect to "+self.SCOMM_HOST+":"+str(self.SCOMM_INFOPORT)+"...")
              return
          else:
            pprint.pprint (sys.exc_info())

          done=0;

          while 1:
            if done:
               break
            data = s.recv(1024).decode('ascii')

            if (len(data)<=0):
              return -1
              break
                
            if 'Connected' in self.scomm:
              del self.scomm['Connected']

            for string in data.split('\n'):
              k=string.split(':')
              if (len(k)==2):
                if k[0]=='Connected' and k[0] in self.scomm.keys():
                    self.scomm[k[0]]=self.scomm[k[0]]+";"+k[1];
                else:
                    self.scomm[k[0]]=k[1];
              else:
                r = re.match("Link(Up|Down)",k[0]);
                if r:
                    if 'Link' in self.scomm and self.scomm['Link']!=r.group(1):
                        self.scomm['LastLinkChanged']=time.strftime("%s", time.localtime())
                    self.scomm['Link']=r.group(1);
                    done=1
                    break

            self.scomm['_timestamp']=time.strftime("%s", time.localtime())

#    output_file = open('/var/www/m200/scomm.json', 'wb')
#    output_file.write(json.dumps(scomm).encode('ascii'));
#    output_file.close()
            s.close()
            print("scomm_get_info() end")
            pprint.pprint(self.scomm)

#            if self.s:
#                pprint.pprint(self.s)

        def connect(self):
            try:
                self.sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sc.connect((self.SCOMM_HOST, int(self.SCOMM_PORT)))
                self.sc.setblocking(0)
            except ConnectionRefusedError:
                print ('could not connect to '+self.SCOMM_HOST+':'+self.SCOMM_PORT)
                return
            pprint.pprint(self.sc.fileno())

            io_loop = tornado.ioloop.IOLoop.current();
            callback = functools.partial(self.recv_from_scomm, self.sc)
            io_loop.add_handler(self.sc.fileno(), callback, io_loop.READ)

            self.groupinfo_request()
            self.pcmstatus_request()

        def disconnect(self):
            self.sc.close()
            dir(self.sc)

        def groupinfo_request(self):
            tornado.ioloop.IOLoop.current().add_timeout(time.time() + 15, lambda:self.groupinfo_request())
            if self.overload: 
               self.sc.send(b'pcmstatus 1\r\npcmstatus 2\r\npcmstatus 3\r\npcmstatus 4\r\npcmstatus 5\r\npcmstatus 6\r\npcmstatus 7\r\npcmstatus 8\r\npcmstatus 9\r\npcmstatus 10\r\npcmstatus 11\r\npcmstatus 12\r\npcmstatus 13\r\npcmstatus 14\r\npcmstatus 15\r\npcmstatus 16\r\n')
            self.overload=0
            self.sc.send(b'groupinfo\r\r')

        def pcmstatus_request(self):
            tornado.ioloop.IOLoop.current().add_timeout(time.time() + 110, lambda:self.pcmstatus_request())
            self.sc.send(b'pcmstatus 1\r\npcmstatus 2\r\npcmstatus 3\r\npcmstatus 4\r\npcmstatus 5\r\npcmstatus 6\r\npcmstatus 7\r\npcmstatus 8\r\npcmstatus 9\r\npcmstatus 10\r\npcmstatus 11\r\npcmstatus 12\r\npcmstatus 13\r\npcmstatus 14\r\npcmstatus 15\r\npcmstatus 16\r\n')

        def recv_from_scomm(self, sock, fd ,events):
            print ("recv_from_scomm()")
            while True:

              try:
                data=sock.recv(2048);
                if len(data)==0:
                    self.sc.close()
                    self.connect()
                    return
              except socket.error as e:
                if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                return

              data=data.decode('cp1251');
              wait_done=0;
              for string in data.split('\n'):
                 if len(string)!=0:
                    print(string)

                 r = re.search("^(CALL|SEIZ|RLSI|RLSO)",string);
                 if r:
                    log(string)
                    continue

                 if wait_done:
                    r=re.search("(---|ERR) (\d+) (\w+) (\w+)",string)
                    if r:
                       self.pcmstatus[pcm]['errors'][r.group(4)]=r.group(2);
                       if r.group(1)=="ERR":
                          self.pcmstatus[pcm]['status']="error";
                          if r.group(4)=="LOS" or r.group(4)=="RRA":
                             self.pcmstatus[pcm]['status']="down";
                       continue

                 r = re.search("(?<=Group) (\d+) - (\d+)/(\d+)",string);
                 if r:
                    self.groupinfo[r.group(1)]=r.group(2)+"/"+r.group(3)
                    if r.group(2)==r.group(3):
                       self.overload=1
                    self.groupinfo['_timestamp']=time.strftime("%s", time.localtime())
                    continue

                 r = re.search("PCM (\d+) protected",string)
                 if r:
                    self.pcmstatus[r.group(1)]={};
                    self.pcmstatus[r.group(1)]['status']="protected";
                    continue

                 r = re.search("PCM (\d+) status bits:",string)
                 if r:
                    self.pcmstatus['_timestamp']=time.strftime("%s", time.localtime())
                    wait_done=1;
                    err='';
                    pcm=r.group(1)
                    self.pcmstatus[pcm]={};
                    self.pcmstatus[pcm]['errors']={};
                    self.pcmstatus[pcm]['status']="normal";
                    continue

                 if re.search("Done",string):
                    wait_done=0;
                    continue


class ScommHandler(tornado.web.RequestHandler):
    def get(self):
        global m200
        self.set_header("Content-Type","application/json")
        self.set_header("Access-Control-Allow-Origin","*")
        ret={}
        r=re.match('^/scomm/(start|stop)',self.request.uri)
        if r:
            if r.group(1)=="start":
              if m200.scomm_start():
                ret={"status":"started"}
              else:
                ret={"status":"not started"}
            else:
              if m200.scomm_stop():
                ret={"status":"stopped"}
              else:
                ret={"status":"not stopped"}

        self.write(json.dumps(ret))

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("/opt/m200/index.html")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global m200
        self.set_header("Content-Type","application/json")
        self.set_header("Access-Control-Allow-Origin","*")

                # scomm status
#        scomm_file = open('/var/www/m200/scomm.json', 'rb')
#        scomm = json.loads(scomm_file.read(8192).decode('ascii'))
#        scomm_file.close()

        # groupinfo
#        groupinfo_file = open('/var/www/m200/groupinfo.json', 'rb')
#        groupinfo = json.loads(groupinfo_file.read(8192).decode('ascii'))
#        groupinfo_file.close()

        # pcmstatus
#        pcmstatus_file = open('/var/www/m200/pcmstatus.json', 'rb')
#        pcmstatus = json.loads(pcmstatus_file.read(8192).decode('ascii'))
#        pcmstatus_file.close()

        dest=dict()
        dest['m200status']={"code":0,"descr":"normal"};
        dest['_timestamp']=timestamp=time.strftime("%s", time.localtime())

        if '_timestamp' in m200.scomm and int(m200.scomm['_timestamp'])<(int(timestamp)-30):
            dest['scomm']={"_error":"scomm.json is old"}
            dest['m200status']={"code":-3,"descr":"scomm is probably down"}
        else:
            dest['scomm']=m200.scomm
            if 'Link' in m200.scomm and m200.scomm['Link']=='Down':
                dest['m200status']={"code":-1,"descr":"scomm link is down"}
        
        if '_timestamp' in m200.groupinfo and int(m200.groupinfo['_timestamp'])<(int(timestamp)-60):
            dest['groupinfo']={"_error":"groupinfo.json is old"}
        else:
            dest['groupinfo']=m200.groupinfo
        
        if '_timestamp' in m200.pcmstatus and int(m200.pcmstatus['_timestamp'])<(int(timestamp)-300):
            dest['pcmstatus']={"_error":"pcmstatus.json is old"}
        else:
            dest['pcmstatus']=m200.pcmstatus
        
        if dest['m200status']['code']==0:
            for pcm in m200.pcmstatus.keys():
                if pcm=="_timestamp":
                    continue;
                if m200.pcmstatus[pcm]["status"]=="down":
                    dest['m200status']={"code":2,"descr":"pcm is down"}
                if m200.pcmstatus[pcm]['status']=="error":
                    dest['m200status']={"code":1,"descr":"active error on pcm"}

        if dest['m200status']['code']==0:
            for gr in m200.groupinfo.keys():
                if gr=="_timestamp":
                    continue;
                (t,b)=m200.groupinfo[gr].split('/')
                if t==b:
                    dest['m200status']={"code":3,"descr":"group is full"}
        
        self.write(json.dumps(dest))

class ConsoleWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.SCOMM_HOST='127.0.0.1'
        self.SCOMM_PORT=10001
        r=re.match('^/console/(\d+)/([0-9.]+)',self.request.uri)
        if r:
            self.SCOMM_HOST=r.group(2)
            self.SCOMM_PORT=r.group(1)
        else:
            r=re.match('^/console/(\d+)',self.request.uri)
            if r:
                self.SCOMM_PORT=r.group(1)
#        pprint.pprint(self.request);

        log("New client connected: ",self.request.remote_ip," to ",self.SCOMM_HOST+":"+str(self.SCOMM_PORT));
        try:
            self.scomm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.scomm.connect((self.SCOMM_HOST,int(self.SCOMM_PORT)))
            self.scomm.setblocking(0)
        except ConnectionRefusedError:
            self.write_message(bytes('WebSocket proxy: could not connect to '+self.SCOMM_HOST+':'+self.SCOMM_PORT+'\r\n','utf8'));
            self.on_close()
            self.close()
            return

        io_loop = tornado.ioloop.IOLoop.current();
        callback = functools.partial(self.on_scomm_message, self.scomm)
        io_loop.add_handler(self.scomm.fileno(), callback, io_loop.READ)



    def on_scomm_message(self, sock, fd ,events):
#        print ("on_scomm_message()")
        while True:
            try:
                data=sock.recv(1024);
                if len(data)==0:
                    self.close()
                    self.scomm.close()
                    return
                data=data.decode('cp1251');
                for str in data.split('\n'):
                    if len(str)!=0:
                        self.write_message(str)
            except socket.error as e:
                if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                return

    def on_message(self, message):
        log(self.request.remote_ip," -> ",self.SCOMM_HOST+":"+str(self.SCOMM_PORT),": ",message);
        self.scomm.send(bytes(message+'\r\n','cp1251'));

    # client disconnected
    def on_close(self):
        log("Client disconnected: ",self.request.remote_ip," from ",self.SCOMM_HOST+":"+str(self.SCOMM_PORT));
        self.scomm.close()

application = tornado.web.Application([
    (r"^/console.*", ConsoleWebSocketHandler),
    (r"^/status", MainHandler),
    (r"^/scomm.*", ScommHandler),
    (r"^/$", IndexHandler),
    (r"^/(.*)", tornado.web.StaticFileHandler,{'path':'/opt/m200'}),
],template_path='/opt/m200',static_path='/opt/m200')


def master_request(response):
    global http_client
    tornado.ioloop.IOLoop.current().add_timeout(time.time() + 5, lambda:http_client.fetch(MASTER, master_request))

    if response.error:
        print ("Error:", response.error)
    else:
        master=json.loads(response.body.decode('ascii'))
#        pprint.pprint(master['m200status']['code'])
#        if master and master['m200status'] and master['m200status']['code']==0:
#            pprint.pprint(master['m200status']['code'])

if __name__ == "__main__":
    m200=M200(SCOMM_HOST,SCOMM_PORT,SCOMM_INFOPORT,SCOMM_PROTV)
    application.listen(8888)

    if 'MASTER' in vars():
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(MASTER, master_request)

    tornado.ioloop.IOLoop.instance().start()
