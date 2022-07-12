#
# This file is part of Python Library for Patches Creator.
# Copyright (C) 2021 INPE.
#
# Python Library for Patches Creator is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Example for Python Library for Patches Creator."""
import os

print('\n'+'='*95)
print('Patch Builder Creator has a Command Line Interface (CLI):')
print('$ patch-builder --help')
print(os.system('patch-builder --help'))

print('\n'+'Or:')
print('='*10)
print('$ patch-builder patch-create --help')
print(os.system('patch-builder patch-create --help'))

print('Usage example:')
print('='*25)
print('$ patch-builder patch-create --access-token <your_token> --collection-id S2-SEN2COR_10_16D_STK-1 --tiles 081094 --datetime 2017-01-01/2017-01-31 --bands red,nir --size 128x128')



