


import subprocess
import socket
import time
import re

const_ricmd1 = '''netstat -n'''
const_ricmd2 = '''netstat -n |findstr "3389"'''
const_ricmd3 = '''netstat |findstr "3389"'''
const_reporttime = 10
const_server_ip = '192.168.1.104'
const_server_port = 9999
const_target_port = "3389"
const_ip_prefix = "192.168.1."


def command(cmd, seconds=5):
    """执行命令cmd，返回命令输出的内容。
    如果超时将会抛出TimeoutError异常。
    cmd - 要执行的命令
    timeout - 最长等待时间，单位：秒
    """
    try:
        # use function check_output will causes another exception
        # Error: Command 'netstat -n |findstr "443"' returned non-zero exit status 1.
        # output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=5)
        ttt = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output,_ = ttt.communicate(timeout = seconds)
    except Exception as e:
        # print('Error:', e)
        ttt.kill()
        output = "timeout"
    return str(output)


def process(cmdstr):
    res ="nobody"
    if cmdstr == "timeout":
        res = "timeout"
    else:
        # print(cmdstr)
        tempstrlist1 = re.split(r"\\r\\n|b'", cmdstr)
        for temp1 in tempstrlist1:                  #TCP    192.168.1.104:54334    180.163.243.184:80     ESTABLISHED
            temp1 = temp1.strip()
            print(temp1)
            tempstrlist2  = re.split(r'\s+', temp1)
            if len(tempstrlist2)!=4:
                print("aaa")
                continue
            tempstrlist3 = re.split(r':', tempstrlist2[1])  #192.168.1.104:54334
            tempstrlist4 = re.split(r':', tempstrlist2[2])  #180.163.243.184:80
            if(len(tempstrlist3)!=2 or len(tempstrlist4)!=2 or tempstrlist3[1] != const_target_port):
                print("bbb")
                continue
            else:
                res = tempstrlist4[0]
    return  res



if __name__ == '__main__':

    alivecount = 1
    my_ip = "unknownip"
    hostname = socket.gethostname()
    addrs = socket.getaddrinfo(hostname, None)
    for item in addrs:
        print(item[4][0])
        if const_ip_prefix in item[4][0]:
            my_ip = item[4][0]


    isconnect = False
    client = socket.socket()
    while True:

        try:
            if  isconnect == False:
                print("try to connect server:"+const_server_ip+":"+str(const_server_port))
                client = socket.socket()
                client.connect((const_server_ip, const_server_port))
                print("connect OK")
                isconnect = True

            ipstring = process(command(const_ricmd2))
            domainstring = process(command(const_ricmd3))

            sendstr = my_ip + "@" + ipstring + "@" + domainstring
            client.send(sendstr.encode())
        except Exception as e:
            print("connect NG,socket close")

            client.close()
            isconnect = False
        finally:
            alivecount = alivecount+1
            print("alivecount"+str(alivecount))
            time.sleep(const_reporttime)



