import json
import requests
import csv
import pandas as pd
import datetime
from . import config


def get_data(URL=None,params=None):
    if URL is None or params is None:
        raise ValueError('RegisterUZ get_data: Missing URL or parameters')
    else:
        try:
            response = requests.get(url = URL, params = params, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as err:
            print(err)
        except json.decoder.JSONDecodeError:
            raise RuntimeError('RegisterUZ get_data: server response is not JSON')

def write_csv(data, name="output"):
#     df = pd.DataFrame.from_dict(data)
#     df.to_csv("output.csv", sep=";")

#     keys = []
#     vals = []
#     for k in data:
#         keys.append(k)
#     keys = sorted(keys)
#     for k in keys:
#         vals.append(data[k])
#     print(data.keys())
#     print(vals)
    if isinstance(name, int):
        name = str(name)
    with open(name+'.csv', 'w',newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys(),delimiter=";")
        writer.writeheader()
        writer.writerow(data)
            
def is_int(val):
    try:
        num = int(val)
    except ValueError:
        return False
    return True 


def uctovna_jednotka(id=0, csv_file=True):
    input_params = {"id":id}
    d = get_data(config.BASE_URL+config.UCTOVNA_JEDNOTKA,input_params)
    if d is not None and csv_file:
        write_csv(d,name=id)
    elif d is not None and not csv_file:
        return d
    return None
        
def uctovne_jednotky(zmenene_od=None,pokracovat_za_id=None,max_zaznamov=None,ico=None,dic=None,pravna_forma=None):
    params = {}

    # kontrola zmenene_od
    if zmenene_od is not None: 
        valid_time = 0
        for f in config.DATE_TIME_FORMATS:
            try:
                date = datetime.datetime.strptime(zmenene_od, f)
                valid_time+=1
            except ValueError as err:
                pass
#                 print(err)
        if valid_time is not 0: 
            params["zmenene-od"] = zmenene_od
        else: 
            raise ValueError('RegisterUZ uctovne_jednotky: zmenene_od is mandatory or incorrect')
#             params["zmenene-od"] = config.DEFAULT_DATE
#             print(f'Parameter zmenene_od={zmenene_od} nie je spravny')
#             print(f'Skontroluj spravnost alebo')
#             print(f'pouzi jeden z {config.DATE_TIME_FORMATS} formatov')
#             print(f'Hodnota zmenene_od bola nastavena na {config.DEFAULT_DATE}')

    # kontrola pokracovat_za_id 
    if pokracovat_za_id is not None:
        if is_int(pokracovat_za_id):
            params["pokracovat-za-id"] = pokracovat_za_id

        
    # kontrola max_zaznamov
    if max_zaznamov is not None:
        if is_int(max_zaznamov):
            check = lambda x: x > 1 and x <= 10000
            if check(int(max_zaznamov)): 
                params["max-zaznamov"] = max_zaznamov
            else:
                raise ValueError('RegisterUZ uctovne_jednotky: max_zaznamov is incorrect')
        else:
            raise ValueError('RegisterUZ uctovne_jednotky: max_zaznamov is incorrect')
    # kontrola ico
    if ico is not None:
        if isinstance(ico,str) and is_int(ico) and len(ico)==8:
            params["ico"] = ico
        else:
            raise ValueError('RegisterUZ uctovne_jednotky: ico is incorrect')
    
    # kontrola dic
    if dic is not None:
        if isinstance(dic,str) and is_int(dic) and len(dic)==10:
            params["dic"] = dic
        else:
            raise ValueError('RegisterUZ uctovne_jednotky: dic is incorrect')
    
    # kontrola pravna_forma
    if pravna_forma is not None:
        if isinstance(pravna_forma,str) and is_int(pravna_forma):
            params["pravna-forma"] = pravna_forma
        else:
            raise ValueError('RegisterUZ uctovne_jednotky: pravna_forma is incorrect')
    

    d = get_data(config.BASE_URL+config.UCTOVNE_JEDNOTKY,params)
    print("uctovne jednotkyyy")
    print(d)