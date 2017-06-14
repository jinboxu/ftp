import socket
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
print(base_dir)
server = socket.socket()
server.bind(('localhost', 6789))
server.listen()
conn,addr = server.accept()

class Ftp_server(object):
    def __init__(self):
        pass_dict = {}
        with open("passwd", 'r', encoding='utf-8') as f:
            for line in f:
                pass_dict[line.split()[0]] = line.split()[1]
        self.user_passwd = pass_dict
        login_eroll = conn.recv(1024).decode()
        conn.send(b"ok")
        getattr(self, login_eroll)()
        # cmd_list = ["get", "upload", "ls", "logout"]
        while True:
            self.cmd_list = eval(conn.recv(1024).decode())
            print(self.cmd_list)
            cmd_name = self.cmd_list[0]
            getattr(self, cmd_name)()
            # if hasattr(self, cmd_name):
            #     # conn.send(b"True")  #!!!!!
            #     getattr(self, cmd_name)
            # else:
            #     conn.send(b"cmd error")

    def login(self):
        while True:
            user_passwd = conn.recv(1024).decode().split()
            print(user_passwd)
            if user_passwd[0] in self.user_passwd and self.user_passwd[user_passwd[0]] == user_passwd[1]:
                conn.send(b"True")
                home_dir = base_dir + os.sep + "home" + os.sep + user_passwd[0] + os.sep
                os.chdir(home_dir)
                break
            else:
                conn.send(b"username or passwd is wrong...")

    def eroll(self):
        while True:
            print(self.user_passwd)
            username = conn.recv(1024).decode()
            if username not in self.user_passwd:
                conn.send(b"True")
                with open("passwd", 'a+', encoding='utf-8') as f:
                    passwd = conn.recv(1024).decode()
                    f.write("\n%s     %s"%(username, passwd))
                self.user_passwd[username] = passwd
                conn.send(b"ok")
                home = base_dir + os.sep + "home" + os.sep
                os.chdir(home)
                os.mkdir(username)
                os.chdir(home + username + os.sep)
                break
            else:
                conn.send("用户名已存在".encode())

    def get(self):
        cmd ,filename = self.cmd_list
        print(filename)
        if os.path.isfile(filename):
            f = open(filename, 'rb')
            file_size = os.stat(filename).st_size
            conn.send( str(file_size).encode() )
            conn.recv(1024)
            for line in f:
                conn.send(line)    #这些连续的发生一般会连着几个一起发送，但这种粘包是正常的 \
                                  #但当后面再有数据发送时（不是同一组数据）,就要注意粘包了（比如传文件时做md5认证）
            f.close()
        else:
            conn.send(b"False")

    def upload(self):
        cmd,filename = self.cmd_list
        print(filename)
        conn.send(b"ready to get file")
        file_total_size = int(conn.recv(1024).decode())
        conn.send(b"get the file size")

        f = open(filename, 'wb')
        received_size = 0
        while received_size <  file_total_size:
            data = conn.recv(1024)
            f.write(data)
            received_size += len(data)
            print(file_total_size, received_size)
        else:
            f.close()
            pass

    def ls(self):
        res = str(os.listdir('.'))
        conn.send( str(len(res.encode())).encode() )
        conn.recv(1024)

        conn.send(res.encode())

    def exit(self):
        pass


if __name__ == '__main__':
    Ftp_server()