import telnetlib
import time

class Device:

    def __init__(self,ip,username,password,tn=None):
        self.ip = ip
        self.username =username
        self.password =password
        self.tn = tn

    def connect(self):
        self.tn=telnetlib.Telnet(self.ip,port='23')

    def authenticate(self):
        self.tn.write(self.username.encode()+ b'\n')
        time.sleep(1)
        self.tn.write(self.password.encode()+ b'\n')

    def send(self,command,timeout=0.5):
        self.tn.write(command.encode() + b'\n')
        time.sleep(timeout)

    def show(self):
        output=self.tn.read_all().decode('utf-8')
        return output

    def read(self,search):
        self.tn.read_until(search,timeout=2)


def send_telnet(ip,username,password,commands,namefile):

    t_end = time.time()+60*10 # 4 minutos

    try:
        while time.time() < t_end:
            D1=Device(ip,username,password)
            D1.connect()

            D1.authenticate()

            D1.send('terminal length 0',1)

            for command in commands:    
                D1.send(command,1)

            D1.send('\n',1)
            D1.send('\n',1)
            D1.send('exit',1)
        

            output= D1.show()
            output_list=output.splitlines() # en listas

            if 'exit' in output_list[-1]:

                with open(f'{namefile}', 'w') as f:
                    for line in output_list:
                        f.write(f'{line}\n')

                return output

            else:

                return 'bad'
    except:
        pass



if __name__ == "__main__":

    #Cambiar ips por reales
    ips=[ 
    
  '8.8.8.8',  
  '8.8.8.8',  
 
  
 
              ]
    for ip in ips:
    
        # Cambiar user y password por credenciales propias
        commands=['show run']
        output=send_telnet(ip,'user','password',commands,f'{ip}_run')
        print(ip)
        print(output)