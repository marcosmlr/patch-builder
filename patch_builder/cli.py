#
# This file is part of Python Library for Patches Creator.
# Copyright (C) 2021 INPE.
#
# Python Library for Patches Creator is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Command line interface for the Patches Creator."""
import click
import timeit

try:
    from .patch_builder import PatchBuilder
except:
    from patch_builder import PatchBuilder
    import os
    os.chdir('..') #goes to the raw path of the package





@click.group()
@click.version_option()
def cli():
    """Patches Creator on command line."""
    pass  # pragma: no cover


@cli.command()
@click.option('--url', default='https://brazildatacube.dpi.inpe.br/stac/', help='The STAC server address (an URL).')
@click.option('--access-token', required=True, help='Personal Access Token of the BDC Auth.')
@click.option('--collection-id', required=True, help='The Collection id. For example CB4_64_16D_STK-1')
@click.option('--tiles', type=click.STRING, required=True, help='Comma delimited tiles.')
@click.option('--datetime', type=click.STRING, required=True, help='Single date, date+time, or a '
                                                                   'range (\'/\' separator), formatted to RFC 3339,'
                                                                   ' section 5.6')
@click.option('--bands', type=click.STRING, required=True, help='Comma delimited common name of bands. For example red,'
                                                                'nir, B07 or all')
@click.option('--size', type=click.STRING, required=True, help='Patch size in pixels. For example 128x128.')
@click.option('--path-output', default='./patch-builder-out/', help='The path to save files.')
@click.option('--cloud', type=click.BOOL, required=True, help='Boolean condition to create patches without downloading'
                                                              'assets previously. If False, raster files will be stored'
                                                              'locally and accelerate new creations of patches from'
                                                              'these images. This is a trade-off between time and'
                                                              'storage consume')
def patch_create(url, access_token, collection_id, tiles, datetime, bands, size, path_output, cloud):
    start = timeit.default_timer()
    kwargs = {'path_output':path_output}
    pb_object = PatchBuilder(url, collection_id, tiles, datetime, bands, size, access_token=access_token,
                             **kwargs)
    if cloud:
        items = pb_object.list_items()
    else:
        items = pb_object.download_items()

    pb_object.patch_items(items)
    print('Total time elapsed (sec):', timeit.default_timer() - start)
    print('See results at {} folder!'.format(kwargs['path_output']))

if __name__ == '__main__':
    # This line is needed to debug the CLI of the package:
    # patch_create(['--access-token', 'your_token', '--collection-id', \
    #               'S2-SEN2COR_10_16D_STK-1', '--tiles', '089096','--datetime','2018-12-19/2018-12-31','--bands', \
    #               'blue', '--size', '128x128', '--cloud', 'False'])
    pass
