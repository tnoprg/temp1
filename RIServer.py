import tornado.ioloop
import tornado.web
import time
import datetime
import numpy as np
import pandas as pd
import threading
import socketserver
import re

df = None
const_socket_ip_port = ("", 9999)
const_web_port = 8888
const_minute_timeout = 1
const_monitor_period = 60

last_monitor_time = ""
class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            while True:
                self.data=self.request.recv(1024)
                print("{} send:".format(self.client_address),self.data)
                if not self.data:
                    print("connection lost")
                    break
                temp = self.data.decode()
                db_recieve_update(temp)
                # self.request.sendall(self.data.upper())
        except Exception as e:
            print(self.client_address,"连接断开")
        finally:
            self.request.close()
    def setup(self):
        print("before handle,连接建立：",self.client_address)
    def finish(self):
        print("finish run  after handle")

# the following function will lead a error!!
# [WinError 10053] but the reason is unknown
# class MyServer(socketserver.BaseRequestHandler):
#     def Handle(self):
#         print("OKOKOKOKOKOaaaaaaaaaaaaaaaaaaa")
#         print("conn is :", self.request)  # conn
#         print("addr is :", self.client_address)  # addr
#
#         while True:
#             try:
#                 # 收消息
#                 print("OKOKOKOKOKObbbbbbbbbbbbbbbbb")
#                 data = self.request.recv(1024)
#                 if not data: break
#                 print("收到客户端的消息是", data.decode("utf-8"))
#                 # 发消息
#                 self.request.sendall(data.upper())
#             except Exception as e:
#                 print(e)
#                 break

def threadfunc_socket():
    s = socketserver.ThreadingTCPServer(const_socket_ip_port, MyTCPHandler)
    s.serve_forever()

def threadfunc_monitor():
    while True:
        db_time_update()
        df.to_csv('machineinfo.csv', index=None)
        time.sleep(const_monitor_period)



def db_init():
    global df
    df = pd.DataFrame(pd.read_csv('machineinfo.csv'))
    print("init db OK")


def get_username(ip,domainname):
    return "AAAAAAAAAAAAA"

def db_recieve_update(str):
    #192.168.1.105@192.168.1.104@timeout
    global df
    tempstrlist = re.split(r"@", str)
    if len(tempstrlist) != 3:
        print("incorrect format:"+str)
        return

    if tempstrlist[2] == "timeout":
        tempstrlist[2] = "unknown"

    for index,row in df.iterrows():
        if row['Machine'] == tempstrlist[0]:
            timestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.loc[index, "LastReportTime"] = timestr
            if get_username(tempstrlist[1],tempstrlist[2]) != df.loc[index, "UserName"]:
                df.loc[index, "LastChangeTime"] = timestr
            df.loc[index, "IsAlive"] = "YES"
            df.loc[index, "DomainName"] = tempstrlist[2]
            df.loc[index, "UserIP"] = tempstrlist[1]
            df.loc[index, "UserName"] = tempstrlist[1]

            #Machine	IsAlive	DomainName	UserIP	User1Name	LastReportTime	LastChangeTime
            return
    print("cannot find machine:"+str)


def db_time_update():
    global df
    global last_monitor_time
    time1 = datetime.datetime.now()
    last_monitor_time = time1
    for index, row in df.iterrows():
        try:
            time2 = datetime.datetime.strptime(row['LastReportTime'], "%Y-%m-%d %H:%M:%S")
            delta = datetime.timedelta(minutes=const_minute_timeout)
            if time1- time2 >delta:
                df.loc[index, "IsAlive"] = "NO"
        except Exception as e:
            df.loc[index, "IsAlive"] = "NO"

def db_setdata(machinename,column,value):
    global df
    for index,row in df.iterrows():
        if row['Machine'] == machinename:
            df.loc[index, column] = value

            break

class MainHandler(tornado.web.RequestHandler):
    global df
    def get(self):
        self.write("Hello, world <br>")
        self.write("timestamp:"+str(datetime.datetime.now())+ "<br>")
        self.write("last_monitor_time:" + str(last_monitor_time) + "<br>")
        self.write('''<table border="1">''')
        self.write('''  <tr>''')
        for cols in df.columns.values:
            self.write('''    <th>'''+cols+'''</th>''')
        self.write('''  </tr>''')
        # ----------------------------------------
        for _, row in df.iterrows():
            self.write('''  <tr>''')
            for cols in df.columns.values:
                self.write('''    <td>'''+str(row[cols])+'''</td>''')
            self.write('''  </tr>''')
        self.write('''</table>''')

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":

    db_init()

    t1 = threading.Thread(target=threadfunc_socket)
    t1.start()

    t2 = threading.Thread(target=threadfunc_monitor)
    t2.start()

    # print(df.info())



    app = make_app()
    app.listen(const_web_port)
    tornado.ioloop.IOLoop.current().start()

#datetime.strptime(str, '%Y-%m-%d')

#datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")