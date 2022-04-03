# Basic URL of API - do not change
BASE_URL = 'https://www.registeruz.sk/cruz-public/api/' 

# Part of API URL to get info about object
UCTOVNA_JEDNOTKA = 'uctovna-jednotka'
# If object was remowed from RegisterUZ, it will have this flag in response
# If this flag is set to ZMAZANÉ, object with this flag will not be in results
# If flag is something else, object will be in results and in CSV file will be empty line
UCTOVNA_JEDNOTKA_STATUS_DELETED = 'ZMAZANÉ'
# list of column names, which will be saved in CSV
UCTOVNA_JEDNOTKA_NAMES = ['id','nazovUJ','mesto','ulica','psc','kraj','okres','sidlo', \
                          'pravnaForma','skNace','ico','dic','datumZalozenia','datumZrusenia', \
                          'datumPoslednejUpravy','velkostOrganizacie','druhVlastnictva', \
                          'konsolidovana','idUctovnychZavierok','idVyrocnychSprav']

# Part of API URL to get multiple companies/objects
UCTOVNE_JEDNOTKY = 'uctovne-jednotky'
# List of column names, which will be saved in CSV of objects
UCTOVNE_JEDNOTKY_NAMES = ['id','nazovUJ','mesto','ulica','psc','kraj','okres','sidlo', \
                          'pravnaForma','skNace','ico','dic','datumZalozenia','datumZrusenia', \
                          'datumPoslednejUpravy','velkostOrganizacie','druhVlastnictva','konsolidovana']
# Datetime formats accepted by API 
DATE_TIME_FORMATS = ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S%z']
# Default Datetime to filter objects, will be used if not specified as parameter
DEFAULT_DATE = '2020-01-01'


##
## CISELNIKY
##
# Part of api URL
PRAVNE_FORMY = 'pravne-formy'
# Column names. Data consists of 3 columns
PRAVNE_FORMY_NAMES = ['kod','nazovSK','nazovEN']

SK_NACE = 'sk-nace'
SK_NACE_NAMES = ['kod','nazovSK','nazovEN']

DRUHY_VLASTNICTVA = 'druhy-vlastnictva'
DRUHY_VLASTNICTVA_NAMES = ['kod','nazovSK','nazovEN']

VELKOSTI_ORGANIZACIE = 'velkosti-organizacie'
VELKOSTI_ORGANIZACIE_NAMES = ['kod','nazovSK','nazovEN']

KRAJE = 'kraje'
KRAJE_NAMES = ['kod','nazovSK','nazovEN']

OKRESY = 'okresy'
OKRESY_NAMES = ['kod','nadradenaLokacia','nazovSK','nazovEN']

SIDLA = 'sidla'
SIDLA_NAMES = ['kod','nadradenaLokacia','nazovSK','nazovEN']


ZDROJE_DAT_TABLE = [
    {'kod':'SUSR', 'nazovSK':'Štatistický úrad Slovenskej republiky'},
    {'kod':'SP', 'nazovSK':'systém štátnej pokladnice'},
    {'kod':'DC', 'nazovSK':'DataCentrum'},
    {'kod':'FRSR', 'nazovSK':'Finančné riaditeľstvo Slovenskej republiky'},
    {'kod':'JUS', 'nazovSK':'Jednotné účtovníctvo štátu'},
    {'kod':'OVSR', 'nazovSK':'Obchodný vestník Slovenskej republiky'},
    {'kod':'CKS', 'nazovSK':'Centrálny konsolidačný systém'},
    {'kod':'SAM', 'nazovSK':'Rozpočtový informačný systém pre samosprávu'}]
ZDROJE_DAT_NAMES = ['kod', 'nazovSK']