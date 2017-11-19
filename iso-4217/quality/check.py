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

    dict_en = load_dict('currencies-en.json', 'en')
    dict_ca = load_dict('currencies-ca.json', 'ca')

    found = 0
    not_found = 0
    input_po = polib.pofile('/home/jordi/sc/calaix-de-sastre/iso-4217/iso_4217-3.76.ca.po')
    for entry in input_po:
        msg_en = entry.msgid
        if msg_en in dict_en:
            found = found + 1
            symbol = dict_en[msg_en]
            catalan_po = entry.msgstr
            if symbol not in dict_ca:
                print('No symbol {0} in catalan dict'.format(symbol))
                continue

            catalan_json =  dict_ca[symbol]
            if catalan_po.lower() != catalan_json.lower():
                print('For {0} ({1}) in PO {2} != {3}'.format(symbol, msg_en, catalan_po, catalan_json))
        
            #print('Found: {0}'.format(msg_en))
        else:
            #print('Not found: {0}'.format(msg_en))
            not_found = not_found + 1

    print('Total: found {0} - not found {1}'.format(found, not_found))
 
if __name__ == "__main__":
    main()
