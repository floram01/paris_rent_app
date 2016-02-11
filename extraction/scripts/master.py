import pandas as pd
from pandas import DataFrame, Series
from urllib2 import urlopen
from bs4 import BeautifulSoup
import requests
import re
import time
import os
from datetime import datetime

from extraction_arrondissements import iter_through, extract_from_one, extract_from_soup

#call the extraction script, n being the number of pages to be extracted
extractions = iter_through(100)

#call the merge script
conso_dir="/Users/Flo/projects/paris_rent/extraction/extractions/arrondisements/consolidated"
archive_dir="/Users/Flo/projects/paris_rent/extraction/extractions/arrondisements/archive"
new_dir="/Users/Flo/projects/paris_rent/extraction/extractions/arrondisements/new"

def load_and_move(from_dir_path, to_dir_path):
    for file in os.listdir(from_dir_path):
        if file.endswith(".csv"):
            file_path = from_dir_path + "/" + str(file)
            to_file_path = to_dir_path + "/" + str (file)  
            output = pd.read_csv(file_path)
            os.rename(file_path,to_file_path)
            return output

old_conso = load_and_move(conso_dir, archive_dir)
print old_conso.shape
new_input_file = load_and_move(new_dir, archive_dir)
print new_input_file.shape

data_concat = pd.concat([old_conso, new_input_file], ignore_index=True)

try:
    data_concat.drop('Unnamed: 0', axis=1, inplace=True)
except ValueError:
    pass

num_duplicates=sum(data_concat.duplicated())
print '{0} duplicates dropped'.format(num_duplicates)

data_concat_clean = data_concat.drop_duplicates()
print '{0} observations in the consolidated dataset'.format(
	data_concat_clean.shape[0])

data_concat_clean['price_surf']=data_concat.price/data_concat.surface
mask_price_anomalies= (data_concat_clean.price_surf >=60) | (data_concat_clean.price_surf <=10)
num_anomalies_price = sum(mask_price_anomalies)
print '{0} anomalies (price/m2 >=60 or <=10) dropped'.format(num_anomalies_price)
data_concat_clean = data_concat_clean[~mask_price_anomalies]
mask_surface_anomalies= data_concat_clean.surface <=10
num_anomalies_surface = sum(mask_surface_anomalies)
print '{0} anomalies (surface <10 m2) dropped'.format(num_anomalies_surface)
data_concat_final = data_concat_clean[~mask_surface_anomalies]


timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
new_conso_path = conso_dir + "/Consolidation_" + timestamp + '.csv'
    
data_concat_final.to_csv(new_conso_path, encoding='utf8', index=False)


