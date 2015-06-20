#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-06-08 16:22:06
# @Author  : Linsir (root@linsir.org)
# @Link    : http://linsir.org
import os
import subprocess, threading, json, re
import tornado.ioloop
import tornado.web
import tornado.websocket


def vmstat():
    memoryKey = ['swpd', 'free', 'buff', 'cache', 'total']
    cpuKey = ['us', 'sy', 'id', 'wa']
    diskKey = ['total', 'used', 'avail', 'percent']
    tempKey = ['cpu', 'gpu']
    space = re.compile('\s+')
    memTotal = subprocess.check_output("cat /proc/meminfo | grep MemTotal | sed 's/\\w*:\\s*\\([0-9]*\\).*/\\1/'", shell = True).strip()
    # print(memTotal)
    # 这个地方要使用 shell = True 的话，需要记得退出的时候关闭子进程
    p = subprocess.Popen(['vmstat', '1', '-n'], stdout = subprocess.PIPE)
    io_loop = tornado.ioloop.IOLoop.instance()
    p.stdout.readline()
    p.stdout.readline()
    for line in iter(p.stdout.readline, ''):

        fields = space.split(line.strip())
        memoryVal = fields[2: 6]
        memoryVal.append(memTotal)
        diskVal = get_disk_space()
        tempVal = [get_cpu_temp(), get_gpu_temp()]
        # print diskVal
        # print tempVal
        result = dict(memory=dict(zip(memoryKey, memoryVal)),
                      cpu=dict(zip(cpuKey, fields[12: 16])),
                      disk=dict(zip(diskKey, diskVal)),
                      temp=dict(zip(tempKey, tempVal)),
                      uptime=get_running_time()
                      )
        result = json.dumps(result)
        # print result
        for client in MonitorHandler.clients:
            # print "sending now"
            io_loop.add_callback(client.write_message, result)

def get_running_time():

    return (str(os.popen("uptime").readline()))

def get_gpu_temp():
    try:
        gpu_temp = os.popen( '/opt/vc/bin/vcgencmd measure_temp' ).readline().replace( 'temp=', '' ).replace( '\'C', '' )
        return  float(gpu_temp)
        # Uncomment the next line if you want the temp in Fahrenheit
        # return float(1.8* gpu_temp)+32
    except:
        return 0

def get_cpu_temp():
    try:
        tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
        cpu_temp = tempFile.read()
        tempFile.close()
        return float(cpu_temp)/1000
    except:
        return 0


def get_disk_space():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])

class MonitorHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def check_origin(self, origin):
        return True
    def open(self):
        MonitorHandler.clients.add(self)
        print('clients: %s online.' % len(MonitorHandler.clients))
    def on_message(self, message):
        pass
    def on_close(self):
        MonitorHandler.clients.remove(self)
        print('clients: ', len(MonitorHandler.clients))

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

settings = {
    'debug': True,
    'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'gzip': True,
}

handlers = [
    (r'/', IndexHandler),
    (r'/ws', MonitorHandler),
]

application = tornado.web.Application(handlers, **settings)

if __name__ == '__main__':
    application.listen(8004)
    t = threading.Thread(target=vmstat)
    t.daemon = True
    t.start()
    tornado.ioloop.IOLoop.instance().start()
