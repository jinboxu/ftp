import socket,os
client = socket.socket()
client.connect(('localhost', 6789))


class Ftp_client(object):
    def __init__(self):
        while True:
            choice = input("login or eroll :").strip()
            if choice == "login" or choice == "eroll":
                break
        client.send(choice.encode())
        client.recv(1024)
        getattr(self, choice)()
        # while True:
        #     self.cmd = input(">>:").strip()
        #     if not self.cmd:continue
        #     client.send(self.cmd.encode())
        #     self.cmd_ack = client.recv(1024).decode()
        #     print("size:",self.cmd_ack)
        #     if self.cmd_ack != "cmd error":
        #         print("111")
        #         getattr(self, self.cmd.split()[0])()
        #     else:
        #         print(self.cmd_ack)
        while True:
            cmd = input(">>:").strip()
            if not cmd:continue
            self.cmd_list= cmd.split()
            print(self.cmd_list)
            if hasattr(self, self.cmd_list[0]):
                getattr(self, self.cmd_list[0])()
            else:
                print("cmd error")

    def login(self):
        while True:
            username = input('username:').strip()
            passwd = input('passwd:').strip()
            user_passwd = "%s     %s" %(username, passwd)
            client.send(user_passwd.encode())
            login_result = client.recv(1024).decode()
            if login_result == "True":
                print("welcome!",username)
                break
            else:
                print(login_result)
        pass

    def eroll(self):
        while True:
            while True:
                username = input("username:").strip()
                client.send(username.encode())
                result = client.recv(1024).decode()
                if result == "True":
                    break
                else:
                    print(result)
            while True:
                passwd = input("passwd:").strip()
                if passwd == "":
                    continue
                break
            client.send(passwd.encode())
            ack_result = client.recv(1024).decode()
            if ack_result == "ok":
                print("注册已完成\n"
                      "欢迎你，%s" %username)
                break
            else:
                print(ack_result)

    def get(self):
        if len(self.cmd_list) == 2:
            client.send(str(self.cmd_list).encode())
            server_reponse = client.recv(1024).decode()
            if server_reponse == "False":
                print("文件不存在")
                return
            print(server_reponse)
            file_total_size = int(server_reponse)
            client.send(b"ready to recv file")

            received_size = 0
            filename = self.cmd_list[1]
            f = open(filename, 'wb')
            while received_size < file_total_size:
                data = client.recv(1024)
                print(data)
                received_size += len(data)    #在传输有空行的文件时，一定要使用len(data)而不是 1024 \
                                                   # （如果每次遇到空行也是加1024，循环很可能在文件接收完之前结束）
                f.write(data)
                print(file_total_size, received_size)
            else:
                print("file recv done")
                f.close()
        else:
            print("cmd error")


    def upload(self):
        if len(self.cmd_list) == 2:
            filename = self.cmd_list[1]
            if os.path.isfile(filename):
                client.send(str(self.cmd_list).encode())
                client.recv(1024)
                f = open(filename, 'rb')
                file_size = os.stat(filename).st_size
                client.send(str(file_size).encode())
                client.recv(1024)
                for line in f:
                    client.send(line)
                f.close()
                print("file upload over")
            else:
                print("无此文件")
        else:
            print("cmd error")

    def ls(self):
        if self.cmd_list == ["ls"]:
            client.send(str(self.cmd_list).encode())
            server_reponse = client.recv(1024).decode()
            print(server_reponse)
            cmd_res_size = int(server_reponse)
            client.send(b"ready to recv cmd res")

            received_size = 0
            received_data = b''
            while received_size < cmd_res_size:
                data = client.recv(1024)
                received_data += data
                received_size += len(data)  #received_size += 1024
                print(cmd_res_size, received_size)
            else:
                print(received_data.decode())
        else:
            print("cmd error")

    def exit(self):
        if self.cmd_list == ["exit"]:
            exit()
        else:
            print("cmd error")


if __name__ == '__main__':
    Ftp_client()
