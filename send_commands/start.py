import ssh
import pingDevice
import function_text
import credential
import threading
import time
import os
import telnet

from pathlib import Path
from datetime import datetime


'''
Este script funciona para enviar comandos a multiples dispositivos, Cisco.
Es asincrono, pero dependiendo de la cantidad de equipos puede saturarse debido a las capacidades del PC, por lo cual es recomendable
ir enviando comando de a 100 dispositivos y validar.

El script realiza tres pasos, el primero saca un backup del dispositivo, el segundo envia los comandos que estan en "1_Comandos.txt", el tercero saca un backup
final.

El resultado se encuentra en la carpeta con la fecha de start del script, dentro de esta se encuentra otra carpeta con la hora realizada y dentro de esta estan tres mas,
una con el backup inicial, la segunda con el resultado, y la tercera con el backup final. Tambien dentro del resultado se encuentra un archivo 1_Resultado.txt en este archivo
se encuentra si el equipo respondio ping o si no.

Nota: Es una primera version, funciona muy bien con ssh, telnet puede mejorar, algunos equipos rechazan la conexión despues de realizar más de dos intentos.
'''


def sendcommands(ip,usernames,passwords,device_types,all_steps,commands,namefile):

    

    print(f'--> Start {ip}')

    
    now = datetime.now()
       
    #Se crea una carpeta con el nombre dd_mm_yy_h_m
    dt_now = now.strftime("%d_%m_%Y")
    hr_now = now.strftime("%H_%M")
    
    #subcarpetas
    subfolder_initial = f"{namefile}/Initial_Run"
    subfolder_final = f"{namefile}/Final_Run"
    subfolder_result = f"{namefile}/Result"

    #subcarpetas
    subfolder_initial_path = Path(f'{subfolder_initial}').mkdir(parents=True, exist_ok=True)
    subfolder_final_path = Path(f'{subfolder_final}').mkdir(parents=True, exist_ok=True)
    subfolder_final_path = Path(f'{subfolder_result}').mkdir(parents=True, exist_ok=True)

    #inicializacion de variables
    correct = 0
    step = 0


    #Verificacion de Ping
    ping=pingDevice.pingDevice(ip)   
    

    
    if ping == 1 :
            #evaluo diferentes tipos de dispositivos
            for device_type in device_types:
                #intento con diferentes contrasenas
                for password in range(len(passwords)):                 

                    step = 0

                    while step <= 2:
         
                        #tiempo de espera necesario para volver a realizar un intento con nuevas credenciales o tipo de dispositivo
                        time.sleep(5)

                        try:

                            #instancia de dispositivo
                            device_ssh = {"device_type": device_type,"host": ip,"username": usernames[password],"password": passwords[password],"read_timeout_override": 90}

                            #envio de comandos y resultado

                            if step == 0: #backup inicial
                                print(f'--> Extrayendo Backup Inicial ssh {ip}')
                                output = ssh.send_show_command(device_ssh, ['show run'],f'{subfolder_initial}/{ip}_initial.txt')                        
                                output_lines=(str(output)).splitlines()
                        
                            
                            elif step == 1 and all_steps == 1: #comandos
                                print(f'--> Enviando Comandos ssh {ip}')
                                output = ssh.send_show_command(device_ssh, commands,f'{subfolder_result}/{ip}_result.txt')                        
                                output_lines=(str(output)).splitlines()
                            
                            elif step == 2 and all_steps == 1: #Backup final
                                print(f'--> Extrayendo Backup Final ssh {ip}')
                                output = ssh.send_show_command(device_ssh, ['show startup-config'],f'{subfolder_final}/{ip}_end.txt')                        
                                output_lines=(str(output)).splitlines()


                            #Tipo de error causado porque no es el tipo de dispositivo correcto
                            if "TCP connection to device failed." in output_lines[0]:                                
                                step = 3
                                break

                            #contrasenas invalidas
                            elif "Authentication failed." in output_lines[-1]:                                
                                step = 3
                                break

                            #usuario de telnet con dominio, se debe de corregir y poder ingresar con usuario de dominio por telnet.
                            elif "Login failed" in output_lines[0]:                                
                                step = 3
                                break
                        
                            #si no entro a los otros errores esta correcto
                            elif len(str(output)) > 100 :                                                    
                                step += 1
                            else :                                
                                step = 3
                                break


                            if step == 3 :
                                correct=1
                                step = 0
                                break

                            #si no tengo nada en los comandos, entonces solo saca el backup inicial
                            if  all_steps == 0 :
                                step = 3
                                correct=1
                                break

                        except(EOFError, ConnectionRefusedError,OSError,ValueError):
                            step = 3                           
                            break
                        except:
                            #aca pasa un error no identificado
                            break
                    
                    if correct == 1:
                        #finaliza el segundo for
                        break

                #si el resultado es correcto no evaluo el siguiente tipo de dispositivo, termino en este punto
                if correct == 1:
                   
                    with open(f'{subfolder_result}/1_Resultado.txt', 'a') as f:
                        f.write(f'{ip};{device_type};correcto\n')

                    break

            if correct == 0:
                telnet_ok = 0
                #Se intenta con la otra secuencia de telnet, para usuario de dominio.
                print(f'Iniciando secuencia telnet {ip}')
                
                for password in range(len(passwords)):
                    print(f'--> Extrayendo Backup Inicial telnet {ip}')    
                    output=telnet.send_telnet(ip,usernames[password],passwords[password],['terminal length 0','show run'],f'{subfolder_initial}/{ip}_initial.txt')

                    if all_steps == 0 and output!=None:
                        telnet_ok = 1
                        with open(f'{subfolder_result}/1_Resultado.txt', 'a') as f:
                            f.write(f'{ip};Telnet;correcto\n')

                        break

                    
                   
                    if output != 'bad' and all_steps == 1:
                        time.sleep(5)
                        print(f'--> Enviando Comandos telnet {ip}')
                        output=telnet.send_telnet(ip,usernames[password],passwords[password],commands,f'{subfolder_result}/{ip}_result.txt')
                        
                        
                    if output != 'bad' and all_steps == 1:
                        time.sleep(5)
                        print(f'--> Extrayendo Backup Final telnet {ip}')    
                        output=telnet.send_telnet(ip,usernames[password],passwords[password],['terminal length 0','show startup-config'],f'{subfolder_final}/{ip}_end.txt')
                        telnet_ok = 1
                        

                        with open(f'{subfolder_result}/1_Resultado.txt', 'a') as f:
                            f.write(f'{ip};Telnet;correcto\n')

                        break

                    

                if telnet_ok == 0 :
                    with open(f'{subfolder_result}/1_Resultado.txt', 'a') as f:
                            f.write(f'{ip};SinConexion;SinConexion\n')
                
               



    else:
        # si no tengo ping, reporto y finalizo
        with open(f'{subfolder_result}/1_Resultado.txt', 'a') as f:
            f.write(f'{ip};sin_ping;fallo\n')
    
    print(f'--> Fin Proceso de {ip}')




if __name__ == "__main__":

        start_time = time.time()
        print('', end="\n")
        print('BIENVENIDO AL MODULO DE CONFIGURACION', end="\n")
        print('POR FAVOR NO OLVIDE CONFIGURAR LOS ARCHIVOS "3_ips.txt" y "1_Comandos.txt', end="\n")
        print('Donde:', end="\n")
        print('     "1_Comandos.txt" corresponde a los comandos que seran enviados a cada dispositivo', end="\n")
        print('     "2_Credenciales.txt" corresponde a las credenciales con las que se probara en cada dispositivo', end="\n")
        print('     "3_ips.txt" corresponde a las ips de los dispositivos que seran configurados', end="\n")
        print('nota:', end="\n")
        print('     Para generar solo backups, ponga las ips en el archivo "3_ips.txt" y deje vacio el archivo "1_Comandos.txt"', end="\n")
        input("Presione ENTER para continuar\n")
        print('---------------------------------------------------------------------------------------------------------------', end="\n")
        
        directory = os.getcwd()

        #toma la fecha actual y la hora para crear carpeta
        now = datetime.now()
        
        #dd_mm_yy_h_m
        dt_now = now.strftime("%d_%m_%Y")
        hr_now = now.strftime("%H%M")
        

        folder = f"{dt_now}"        
        subfolder = f'{folder}/Backup_{hr_now}'
        
        folder_path = Path(f"{folder}" ).mkdir(parents=True, exist_ok=True)
        subfolder_path = Path(f'{subfolder}').mkdir(parents=True, exist_ok=True)
        
        print('Por favor VERIFIQUE los comandos y la cantidad de ips  antes de iniciar el proceso automatico', end="\n")      

        ips=function_text.text_list("3_ips.txt")       
        commands=function_text.text_list("1_Comandos.txt")

        print(f'Commands')
        for command in commands:
            print(f' {command}')
        
        print('', end="\n")
        print(f'Dispositivos: ', len(ips))
        print('', end="\n")

        if len(commands) ==0:
            print('NO TIENE COMANDOS DISPONIBLES, DESEA SACAR SOLO EL BACKUP?', end="\n")
            all_steps = 0
        else:
            all_steps = 1

        
        input("Presione ENTER para INICIAR, si no, cierre la terminal\n")
        print('', end="\n")
        print('---------------------------------------------------------------------------------------------------------------', end="\n")

        usernames = credential.search('usernames')
        passwords = credential.search('passwords')

        device_types = ["cisco_ios","cisco_ios_telnet","cisco_xe"]
        
        print('!!!CONECTANDO!!!', end="\n")
        print('', end="\n")
        #Funcion asincrona
        threads = list()

        for ip in ips:                    
            th = threading.Thread(target=sendcommands, args=(ip,usernames,passwords,device_types,all_steps,commands,f'./{subfolder}'))
            threads.append(th)
            th.start()

        for index, thread in enumerate(threads):
            thread.join()

        end_time = time.time()
        python_execution = round(end_time-start_time,2)
       

        
        print('', end="\n")
        print('Tiempo de ejecucion: ',python_execution,' s')
        input('Presione Enter para Finalizar\n')


        
            
        
