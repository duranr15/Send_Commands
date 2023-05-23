from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
    
    
)


'''
Script para conectarse por ssh
'''


def send_show_command(device, commands,namefile):
    
    
    try:

        
        with ConnectHandler(**device,fast_cli=False) as ssh:

            ssh.enable()
            
            for command in commands:                
                
                output = ssh.send_command(command,read_timeout=90,expect_string=r"#",delay_factor=30)                
                result = output


            ssh.disconnect()

            
            with open(f'{namefile}', 'w') as f:
                f.write(output)

    

        return result
    except (NetmikoTimeoutException, NetmikoAuthenticationException,) as error:
        #'Error netmiko autentication'
        result= 'Authentication failed.'


if __name__ == "__main__":


    device1 = {
        "device_type": "cisco_ios",
        "host": "8.8.8.8",
        "username": "user",
        "password": "password",
        "read_timeout_override": 90,
        
        
    }

    commands1= [
        'terminal length 0',
        'show version'
         ]

    commands2= [
        'terminal length 0',
        'show run'
         ]

    result = send_show_command(device1, commands1,'NameFile')
    print('-->',result)

    result = send_show_command(device1, commands2,'NameFile')
    print('-->',result)

