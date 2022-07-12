#
# This file is part of Python Library for Patches Creator.
# Copyright (C) 2021 INPE.
#
# Python Library for Patches Creator is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Example for Python Library for Patches Creator."""
import argparse
import os
import pprint
import json
import subprocess



def collectionPrettyPrint(collection):
    printData = pprint.PrettyPrinter(indent = 3, width = 75, compact = False)
    printData.pprint(collection)

    
def collectionsInfo(res):
    if '--collection-id' in  args.str_cmd:
                     print('-'*70 + '\n')
                     print(res['title'],'-',res['bdc:metadata']['datacite']['descriptions'][0]['description'])
                     print('\nStart date:',res['extent']['temporal']['interval'][0][0], \
                           'End-date:',res['extent']['temporal']['interval'][0][1])
                     print('\nBands:',res['cube:dimensions']['bands']['values'])
                     print('\nSpatial Extent:',res['extent']['spatial']['bbox'])
                     

    items = [id for id in res]    
    opc = "NaN"
    while opc != 'quit':
        while not opc.isnumeric() and opc != 'quit':
            print('\n'+'-'*70 + '\n')   
            print('Please, choose one key to see further information:')
            for i,id in enumerate(items):
                print(i,'-',id)
            opc = input('Type quit or number -> ')
       
        if opc == 'quit':
            break
        elif 0 <= int(opc) < len(res):
                print('-'*70 + '\n')               
                collectionPrettyPrint(res[items[int(opc)]])
                
        opc = "NaN"



# Create the parser
my_parser = argparse.ArgumentParser(allow_abbrev=False, description='List Catalogs and Collections from Brazil Data Cube project')

# Add the arguments
my_parser.add_argument('--str_cmd', action='store', help='Command Line options to STAC.')

# Execute the parse_args() method
args = my_parser.parse_args()



# main
if args.str_cmd:
    # This is our shell command, executed by Popen.
    data = subprocess.Popen(args.str_cmd, stdout=subprocess.PIPE, shell=True)
    try:
        collectionsInfo(json.loads(data.communicate()[0].decode('utf-8')))
    except ValueError as err:
        print("The string command passed through the '--str_cmd' option, does not return a JSON object valid!")

else:
    print('\n'+'='*95)
    print('Catalogs at https://brazildatacube.dpi.inpe.br/stac/:')
    os.system("stac catalog --url https://brazildatacube.dpi.inpe.br/stac/")
    
    print('\n'+'='*95)
    print('We can use some of these options to retrieve further information about collections from BDC:')
    print('='*95)
    os.system("stac --help")

    
    print('\n\nFor example:')
    print('='*15)
    print("python stac_cli_examples.py --str_cmd 'stac collection --url https://brazildatacube.dpi.inpe.br/stac/ --collection-id CB4_64_16D_STK-1'")

    print('\n\nOr:')
    print('='*5)
    print('stac collection --help')
