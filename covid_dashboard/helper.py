import pycountry_convert as pc
import pycountry
import pandas as pd
import numpy as np

def convert_to_mil_thousand(number):
    
    str_numbered = str(number)
    
    if len(str_numbered) > 6:
        if len(str_numbered) == 7:
            return f"{str_numbered[0]}.{str_numbered[1:4]} M"
        elif len(str_numbered) == 8:
            return f"{str_numbered[0:2]}.{str_numbered[2:5]} M"
        else:
            return f"{str_numbered[0:3]}.{str_numbered[3:6]} M"
        
    elif len(str_numbered) > 3:
        if len(str_numbered) == 4:
            return f"{str_numbered[0]},{str_numbered[1:]}"
        elif len(str_numbered) == 5:
            return f"{str_numbered[0:2]},{str_numbered[2:]}"
        else:
            return f"{str_numbered[0:3]}.{str_numbered[3:]} K"
        
    else:
        return str_numbered


def get_country_code(country_name):
    try:
        return pc.country_name_to_country_alpha2(country_name)
    except:
        pass
    
def get_continent_code(country_code):
    try:
        return pc.country_alpha2_to_continent_code(country_code)
    except:
        pass
    
def get_continent_name(continent_code):
    try:
        return pc.convert_continent_code_to_continent_name(continent_code)
    except:
        pass

def make_it_smaller(df):
    
    df.columns = map(str.lower, df.columns)
    return df

