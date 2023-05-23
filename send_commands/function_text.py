def text_list(name):
        text_list2=list()
    # toma un archivo de texto y devuelve las columnas en una lista
        with open(f'{name}', 'r') as f:
            text=f.read()

        text_list=(str(text)).splitlines()
        
        for item in text_list:
            if len(item) > 0:
                text_list2.append(item)

        return text_list2


    