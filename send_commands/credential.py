import re

def search(word):
    with open(f'2_Credenciales.txt', 'r') as f:
        file=f.read().splitlines()

    for line in file :
        if word in line:
            # print('palabra',line)
            look=re.findall(f'^{word}=(.+)',line)
            looks=look[0].split(',')
            # looks.remove('')
            
            

    return looks

if __name__ == "__main__":     

    print(search('usernames'))
    print(search('passwords'))