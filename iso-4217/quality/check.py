#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import polib

def load_dict(filename, language):

    en_file = open(filename)
    data = json.load(en_file)
    currencies = data['main'][language]['numbers']['currencies']

    result = dict()    
    for currency in currencies.values():
        name= currency['displayName']
        symbol = currency['symbol']
        if language == 'en':
            result[name] = symbol
        else:
            result[symbol] = name
            
        #print('{0} -> {1}'.format(currency['symbol'], currency['displayName']))

    return result

def main():

    forms = [1,2,3,4,5,6,7]
    for form in forms[-1:]:
        print(form)
    
if __name__ == "__main__":

    main()
