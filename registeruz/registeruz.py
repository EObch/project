import json
import requests
import csv
import pandas as pd
import datetime
from . import config
import asyncio
import aiohttp
from aiohttp import ClientSession
import time



async def get_one(session:ClientSession,URL=None,params=None):  
    '''
    Worker function for aiohttp requests
    Parameters:
        CienSession session = generated session check docs at: https://docs.aiohttp.org/en/stable/http_request_lifecycle.html#aiohttp-request-lifecycle
        str URL = URL to make request
        dict params = dictionary of parameters to use
    Return:
        dictionary of data from JSON response
        or Raised error, if some problems with communication or requests
    '''
    try:
        response = await session.request(method='GET', url=URL,params=params)
        response.raise_for_status()
#         print(f"Response status ({URL}): {response.status}")
        response_json = await response.json()
        return response_json
    except requests.exceptions.HTTPError as errh:
        raise RuntimeError(errh)
    except requests.exceptions.ConnectionError as errc:
        raise RuntimeError(errc)
    except requests.exceptions.Timeout as errt:
        raise RuntimeError(errt)
    except requests.exceptions.RequestException as err:
        raise RuntimeError(err)
    except json.decoder.JSONDecodeError:
        raise RuntimeError('RegisterUZ get_data: server response is not JSON')
    except Exception as err:
        raise RuntimeError(f"An error ocurred: {err}")


async def get_data(URL=None,params=None, IDlist=None):
    '''
    Get data from server - faster version
    Parameters:
        str URL = URL usually it is BASE_URL+SPECIFIC_PART_OF_API
        dict params = dictionary of parameters to pass with URL
        list IDlist = list of ID to get from server, If not used (None) there will be only one request with params
    Return:
        list of dict of collected data
        if used with IDlist=None, one dict in list, to access use index 0
        if used with IDlist, number of dictionaries will be length of IDlist
    '''
    if URL is None or params is None:
        raise ValueError('RegisterUZ get_data: Missing URL or parameters')
    elif IDlist is None:
#         connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession() as session:
            tasks = []
#             for url in urls:
            task = asyncio.ensure_future(get_one(session=session,URL=URL,params=params))
            tasks.append(task)
            res = await asyncio.gather(*tasks,return_exceptions=True)
            return res
    elif IDlist is not None:
        connector = aiohttp.TCPConnector(limit_per_host=100)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for i in IDlist:
                task = asyncio.ensure_future(get_one(session=session,URL=URL,params={"id":i}))
                tasks.append(task)
                res = await asyncio.gather(*tasks,return_exceptions=True)
            return res

# old version, not used
def get_data_old(URL=None,params=None):
    '''
    Use to get data from RegisterUZ - not used, is slower for big datasets
    Parameters:
        str URL = URL which will accept GET request
        dict params = dictionary of parameters for specific API call
    Return:
        response of data in JSON format or will raise an error
    '''
    if URL is None or params is None:
        raise ValueError('RegisterUZ get_data: Missing URL or parameters')
    else:
        try:
            response = requests.get(url = URL, params = params, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as errh:
            raise RuntimeError(errh)
        except requests.exceptions.ConnectionError as errc:
            raise RuntimeError(errc)
        except requests.exceptions.Timeout as errt:
            raise RuntimeError(errt)
        except requests.exceptions.RequestException as err:
            raise RuntimeError(err)
        except json.decoder.JSONDecodeError:
            raise RuntimeError('RegisterUZ get_data: server response is not JSON')

def write_csv(data, name="output",writing=None, columns=None):
    '''
    Use to save json data to CSV file
    Parameters:
        dict data = data to write
        str name = name of file to which save data e.g. 'uctovne_jednotky', without extension
    '''
    if isinstance(name, int):
        name = str(name)
    if writing is None or columns is None:
        raise ValueError('RegisterUZ write_csv: Missing parameter: writing')
    elif writing is 'one':
        df = pd.DataFrame([data],columns=columns)
        df.to_csv(name+'.csv',sep=';',index=False,encoding='utf-8-sig')
    elif writing is 'list': 
        df = pd.DataFrame(data,columns=columns)
        df.to_csv(name+'.csv',sep=';',index=False,encoding='utf-8-sig')
       
    elif writing is 'df':        
        data.to_csv(name+'.csv',sep=';',index=False,encoding='utf-8-sig')
        

            
def is_int(val):
    '''
    Use to check if param val is numeric or not
    Parameters:
        anytype val = data to check
    Return:
        False = if conversion fails (not numeric data) 
        True = val is numeric data
    '''
    try:
        num = int(val)
    except ValueError:
        return False
    return True 


def uctovna_jednotka(id=0, csv_file=True):
    '''
    Get info about company by ID
    Parameters:
        str or int id = ID of company in database e.g. 302525
        bool csv_file = True to save data into csv with id name e.g. 302525.csv, False to get JSON data
    Return:
        None = No information for this ID
        JSON = information in JSON format if csv_file = False
    '''
    if id is 0:
        raise ValueError('RegisterUZ uctovna jednotka: Missing parameter: id')
    input_params = {"id":id}
    d = asyncio.run(get_data(config.BASE_URL+config.UCTOVNA_JEDNOTKA,input_params))
    d = d[0]
#     d = get_data_old(config.BASE_URL+config.UCTOVNA_JEDNOTKA,input_params)
    
    if 'stav' in d:
        if d['stav'] == config.UCTOVNA_JEDNOTKA_STATUS_DELETED:
            print(f'Returned data for ID: {id} are: {d["stav"]} ')
            return None
    if d is not None and csv_file:
        write_csv(d,name=id,writing="one", columns=config.UCTOVNA_JEDNOTKA_NAMES)
        print(f'CSV was created with name {id}.csv')
    elif d is not None and not csv_file:
        print(f'Returning data associated with ID {id} ')
        return d
    return None
        
    
def uctovne_jednotky_id_list(params=None):
    '''
    Use only in function uctovne_jednotky
    Use to get list of IDs based on params
    Parameters:
        dict = dictionary of parameters to filter data
    Return:
        List of IDs returned from API based on params
    '''
    if params is not None:
        res = []
        d = asyncio.run(get_data(config.BASE_URL+config.UCTOVNE_JEDNOTKY,params))
        d = d[0]
#         d = get_data(config.BASE_URL+config.UCTOVNE_JEDNOTKY,params)
        res = d["id"]
        if d["existujeDalsieId"]:
            maxval = max(d["id"])
            params["pokracovat-za-id"] = maxval
            params["max-zaznamov"] = 10000
            result = uctovne_jednotky_id_list(params)
            res.extend(result)
            return res
        elif not d["existujeDalsieId"]:
            return res
    
    
def uctovne_jednotky(zmenene_od=None,pokracovat_za_id=None,max_zaznamov=None,ico=None,dic=None,pravna_forma=None,csv_file=True,csv_name='dataset'):
    '''
    Use to get data about companies, based on parameters
    Parameters:
        str zmenene_od = start date to filter data formats: '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S%z' e.g. '2015-01-01'
        str pokracovat_za_id = optional parameter, start filter from some ID e.g. '1'
        str max_zaznamov = optional parameter, number of ID to get back from request, number in range 1,10000 e.g. '100'
        str ico = optional parameter, (Identifikačné čislo organizácie) Identification number of company in SK e.g. '00691135'
        str dic = optional parameter, (Daňové identifikačté číslo) Tax identification number in SK e.g. '2020216748'
        str pravna_forma = ID of type of object e.g. '601' list at https://www.registeruz.sk/cruz-public/api/pravne-formy
        bool csv_file= True, create csv with filtered objects, False will return only list of IDs from DB
        str csv_name = name of dataset which will be created, default is 'dataset'
    Return:
        list of IDs if param csv_file is set to False or nothing, if csv_file=True to create csv file
    '''
    params = {}

    # check zmenene_od
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

    # check pokracovat_za_id 
    if pokracovat_za_id is not None:
        if is_int(pokracovat_za_id):
            params["pokracovat-za-id"] = pokracovat_za_id

        
    # check max_zaznamov
    if max_zaznamov is not None:
        if is_int(max_zaznamov):
            check = lambda x: x > 1 and x <= 10000
            if check(int(max_zaznamov)): 
                params["max-zaznamov"] = max_zaznamov
            else:
                raise ValueError('RegisterUZ uctovne_jednotky: max_zaznamov is incorrect')
        else:
            raise ValueError('RegisterUZ uctovne_jednotky: max_zaznamov is incorrect')
    # check ico
    if ico is not None:
        if isinstance(ico,str) and is_int(ico) and len(ico)==8:
            params["ico"] = ico
        else:
            raise ValueError('RegisterUZ uctovne_jednotky: ico is incorrect')
    
    # check dic
    if dic is not None:
        if isinstance(dic,str) and is_int(dic) and len(dic)==10:
            params["dic"] = dic
        else:
            raise ValueError('RegisterUZ uctovne_jednotky: dic is incorrect')
    
    # check pravna_forma
    if pravna_forma is not None:
        if isinstance(pravna_forma,str) and is_int(pravna_forma):
            params["pravna-forma"] = pravna_forma
        else:
            raise ValueError('RegisterUZ uctovne_jednotky: pravna_forma is incorrect')
    
 

    # get list of ID to retrieve data for them
    idlist = uctovne_jednotky_id_list(params)
    # if list is empty
    if not idlist: raise ValueError('RegisterUZ uctovne_jednotky: No data found for specified filters')
    
#     print(f'Data of length {len(idlist)} with smallest ID {min(idlist)} and biggest ID {max(idlist)}')
    # some data to save
    if csv_file:
        print(f'Downloading...')
        s = time.time()
        d = asyncio.run(get_data(config.BASE_URL+config.UCTOVNA_JEDNOTKA,params={},IDlist=idlist))
        
        # pop deleted ID from list, if object was deleted, records looks like https://www.registeruz.sk/cruz-public/api/uctovna-jednotka?id=1956418
        # simply filter records which do not have key 'stav'
        d = [i for i in d if not 'stav' in i]

        e = time.time()
        write_csv(d,name=csv_name,writing="list",columns=config.UCTOVNE_JEDNOTKY_NAMES)
        
        print(f'Downloaded in: {e-s:.2f} seconds')
        print(f'CSV was created with name {csv_name}.csv and {len(d)} records')

        # slower, not used
#         s = time.time()
#         dataset = []
#         for i in idlist:
#             tmp = uctovna_jednotka(i, csv_file=False)
#             if tmp is not None:
#                 dataset.append(tmp)
#         e = time.time()
#         write_csv(dataset,name="uctovne_jednotky_data",writing="ujlist")
    else: 
        print(f'Returning sorted list of {len(idlist)} numbers')
        return idlist
    
    
    
    
##
## CISELNIKY
##
def pravne_formy(csv_file=True):
    '''
    Get data of: pravne_formy
    Parameters:
        bool csv_file = if you want csv file use True, if want raw JSON use False, default is True
    Return:
        if csv_file is True no return, CSV was created
        if csv_file is False return list of dictionaries
    '''
    data = asyncio.run(get_data(config.BASE_URL+config.PRAVNE_FORMY,{}))
    if csv_file:
        print(f'returning pravne_formy.csv')
        data = data[0]['klasifikacie']
        data = sorted(data, key = lambda i: i['kod'])
        flat = [{'kod':d['kod'],'nazovSK':d['nazov']['sk'],'nazovEN':d['nazov']['en'] }for d in data]
        
        write_csv(flat,name='pravne_formy',writing="list",columns=config.PRAVNE_FORMY_NAMES)
    else:
        print(f'returning json data')
        return data[0]
    

def sk_nace(csv_file=True):
    '''
    Get data of: sk_nace
    Parameters:
        bool csv_file = if you want csv file use True, if want raw JSON use False, default is True
    Return:
        if csv_file is True no return, CSV was created
        if csv_file is False return list of dictionaries
    '''
    data = asyncio.run(get_data(config.BASE_URL+config.SK_NACE,{}))
    if csv_file:
        print(f'returning sk_nace.csv')
        data = data[0]['klasifikacie']
        data = sorted(data, key = lambda i: i['kod'])
        flat = [{'kod':d['kod'],'nazovSK':d['nazov']['sk'],'nazovEN':d['nazov']['en'] }for d in data]
        
        write_csv(flat,name='sk_nace',writing="list",columns=config.SK_NACE_NAMES)
    else:
        print(f'returning json data')
        return data[0]
    
    
def druhy_vlastnictva(csv_file=True):
    '''
    Get data of: druhy_vlastnictva
    Parameters:
        bool csv_file = if you want csv file use True, if want raw JSON use False, default is True
    Return:
        if csv_file is True no return, CSV was created
        if csv_file is False return list of dictionaries
    '''
    data = asyncio.run(get_data(config.BASE_URL+config.DRUHY_VLASTNICTVA,{}))
    if csv_file:
        print(f'returning druhy_vlastnictva.csv')
        data = data[0]['klasifikacie']
        data = sorted(data, key = lambda i: i['kod'])
        flat = [{'kod':d['kod'],'nazovSK':d['nazov']['sk'],'nazovEN':d['nazov']['en'] }for d in data]
        
        write_csv(flat,name='druhy_vlastnictva',writing="list",columns=config.DRUHY_VLASTNICTVA_NAMES)
    else:
        print(f'returning json data')
        return data[0]
    

def velkosti_organizacie(csv_file=True):
    '''
    Get data of: velkosti_organizacie
    Parameters:
        bool csv_file = if you want csv file use True, if want raw JSON use False, default is True
    Return:
        if csv_file is True no return, CSV was created
        if csv_file is False return list of dictionaries
    '''
    data = asyncio.run(get_data(config.BASE_URL+config.VELKOSTI_ORGANIZACIE,{}))
    if csv_file:
        print(f'returning velkosti_organizacie.csv')
        data = data[0]['klasifikacie']
        data = sorted(data, key = lambda i: i['kod'])
        flat = [{'kod':d['kod'],'nazovSK':d['nazov']['sk'],'nazovEN':d['nazov']['en'] }for d in data]
        
        write_csv(flat,name='velkosti_organizacie',writing="list",columns=config.VELKOSTI_ORGANIZACIE_NAMES)
    else:
        print(f'returning json data')
        return data[0]
    
    
def kraje(csv_file=True):
    '''
    Get data of: kraje
    Parameters:
        bool csv_file = if you want csv file use True, if want raw JSON use False, default is True
    Return:
        if csv_file is True no return, CSV was created
        if csv_file is False return list of dictionaries
    '''
    data = asyncio.run(get_data(config.BASE_URL+config.KRAJE,{}))
    if csv_file:
        print(f'returning kraje.csv')
        data = data[0]['lokacie']
        data = sorted(data, key = lambda i: i['kod'])
        flat = [{'kod':d['kod'],'nazovSK':d['nazov']['sk'],'nazovEN':d['nazov']['en'] }for d in data]
        
        write_csv(flat,name='kraje',writing="list",columns=config.KRAJE_NAMES)
    else:
        print(f'returning json data')
        return data[0]
    
    
def okresy(csv_file=True):
    '''
    Get data of: okresy
    Parameters:
        bool csv_file = if you want csv file use True, if want raw JSON use False, default is True
    Return:
        if csv_file is True no return, CSV was created
        if csv_file is False return list of dictionaries
    '''
    data = asyncio.run(get_data(config.BASE_URL+config.OKRESY,{}))
    if csv_file:
        print(f'returning okresy.csv')
        data = data[0]['lokacie']
        data = sorted(data, key = lambda i: i['kod'])
        flat = [{'kod':d['kod'],'nadradenaLokacia':d['nadradenaLokacia'],'nazovSK':d['nazov']['sk'],'nazovEN':d['nazov']['en'] }for d in data]
        
        write_csv(flat,name='okresy',writing="list",columns=config.OKRESY_NAMES)
    else:
        print(f'returning json data')
        return data[0]
    
    
def sidla(csv_file=True):
    '''
    Get data of: sidla
    Parameters:
        bool csv_file = if you want csv file use True, if want raw JSON use False, default is True
    Return:
        if csv_file is True no return, CSV was created
        if csv_file is False return list of dictionaries
    '''
    data = asyncio.run(get_data(config.BASE_URL+config.SIDLA,{}))
    if csv_file:
        print(f'returning sidla.csv')
        data = data[0]['lokacie']
        data = sorted(data, key = lambda i: i['kod'])
        flat = [{'kod':d['kod'],'nadradenaLokacia':d['nadradenaLokacia'],'nazovSK':d['nazov']['sk'],'nazovEN':d['nazov']['en'] }for d in data]
        
        write_csv(flat,name='sidla',writing="list",columns=config.SIDLA_NAMES)
    else:
        print(f'returning json data')
        return data[0]
    

def zdroje_dat(csv_file=True):
    '''
    Get data of: zdroje_dat, no API available
    Exists only in config file, from https://www.registeruz.sk/cruz-public/home/api#datasources
    Parameters:
        bool csv_file = if you want csv file use True, if want raw JSON use False, default is True
    Return:
        if csv_file is True no return, CSV was created
        if csv_file is False return list of dictionaries
    '''
    if csv_file:
        print(f'returning zdroje_dat.csv')
        write_csv(config.ZDROJE_DAT_TABLE,name='zdroje_dat',writing="list",columns=config.ZDROJE_DAT_NAMES)
    else:
        print(f'returning json data')
        return config.ZDROJE_DAT_TABLE
    