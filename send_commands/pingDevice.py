import subprocess
import threading

#modulo para realizar ping 

def pingDevice(ip):        
        
        try:
            ping= 0
            output = subprocess.Popen('ping -n 4 '+ip,stdout=subprocess.PIPE)
            output.wait()
            if output.poll(): 
                # ping DOWN                   
                ping = 0
                
            else: 
                #ping UP                   
                ping = 1
                    
            
            return ping 
        except:
            ping= 0
            return ping


if __name__== "__main__":
    
    #Pink a toda una red
        
    threads2 = list()   
        
    for item in range(1,254): 
        ip= f'10.10.10.{item}'         
        th = threading.Thread(target=pingDevice, args=(ip,))
        threads2.append(th)
        th.start()

    for index, thread in enumerate(threads2):
        thread.join()