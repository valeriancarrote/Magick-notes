import requests
import json
from datetime import datetime
import time 
from token_generator import token_genrator
from date_generator import gen_date

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.ecoledirecte.com',
    'priority': 'u=1, i',
    'referer': 'https://www.ecoledirecte.com/',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-token': token_genrator(),
}

params = {
    'verbe': 'get',
    'v': '4.67.5',
}

#data = 'data={\n    "dateDebut": "2024-12-10",\n    "dateFin": "2024-12-10",\n    "avecTrous": false\n}'
data = f'data={{\n    "dateDebut": "{gen_date()}",\n    "dateFin": "{gen_date()}",\n    "avecTrous": false\n}}'

response = requests.post('https://api.ecoledirecte.com/v3/E/8822/emploidutemps.awp', params=params, headers=headers, data=data)
#print(response.text)
"""
h_date = []
def trans_start(here):  
    
    for object in here:
        #object[:11]        
        obs = object.replace(object[:11], '')
        obse = obs.replace(obs[-3:], '')
        #print(obse)
        h_date.append(obse)
"""
d_date = []
def trans_end(here):  
    
    for object in here:
        #object[:11]        
        obs = object.replace(object[:11], '')
        #obse = obs.replace(obs[-3:], '')
        #print(obse)
        d_date.append(obs)
        

#print(response.text)
json_temp = response.text
y = json.loads(json_temp)
#print(y["data"][0:]["matiere"])
#start_h = [d['start_date'] for d in y['data']]
end_h = [d['end_date'] for d in y['data']]
#trans_start(start_h)
trans_end(end_h)
#print(start_h)
#print(end_h)
now = datetime.now()
heur = now.strftime("%H")
minute = now.strftime("%M")
seconde = now.strftime("%S")
heu = (heur,":",minute,":",seconde)
heure = "".join(heu)
m = []
for d in d_date: 
    if heure < d:
        m.append(d)
heure_de_fin = (min(m))
#print("l'heure de fin est de : ", heure_de_fin)
#print("l'heure actuelle est de : ", heure )
vrais_heure_de_fin = heure_de_fin + ":00"

fini = False 
format_heure = "%H:%M:%S"
heure_obj = datetime.strptime(heure, format_heure)
heure_fin_obj = datetime.strptime(vrais_heure_de_fin, format_heure)
def compte_a_rebours(difference):
    total_secondes = int(difference.total_seconds())
    
    while total_secondes > 0:
        heures = total_secondes // 3600
        minutes = (total_secondes % 3600) // 60
        secondes = total_secondes % 60
        
        print(f"\rTemps restant : {heures:02d}:{minutes:02d}:{secondes:02d}", end="")
        time.sleep(1)
        total_secondes -= 1
        
difference = heure_fin_obj - heure_obj
#print(difference)
compte_a_rebours(difference)

#while fini == False: 


        