#
# This file is part of Python Library for Patches Creator.
# Copyright (C) 2021 INPE.
#
# Python Library for Patches Creator is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Command line interface for the Patches Creator."""
import click

from .patch_builder import PatchBuilder


@click.group()
@click.version_option()
def cli():
    """Patches Creator on command line."""
    pass  # pragma: no cover


@cli.command()
def test():
    click.secho('Test click2', bold=True, fg='green')


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
def patch_create(url, access_token, collection_id, tiles, datetime, bands, size, path_output):
    kwargs = {'path_output':path_output}
    pb_object = PatchBuilder(url, collection_id, tiles, datetime, bands, size, access_token=access_token,
                             **kwargs)

    #items = pb_object.list_items()
    items = pb_object.download_items()
    pb_object.patch_items(items)

