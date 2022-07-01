#
# This file is part of Python Library for Patches Creator.
# Copyright (C) 2021 INPE.
#
# Python Library for Patches Creator is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Define Patch Builder business interface."""
import stac
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import HTTPError
import os
import jsonpath_rw_ext as jp  # for calling extended methods
from multiprocessing import cpu_count
import concurrent.futures
import threading
import rasterio
import timeit
from time import sleep


num_workers = int(cpu_count() * 2)


def url_response(url):
    """Download Assets using URL address.

    :param url: Path output to download file and URL for the Asset
    :type url: tuple
    """
    path_out, url = url
    filename = os.path.join(path_out, urlparse(url)[2].split('/')[-1])
    if not os.path.exists(filename):
        try:
            response = stac.Utils.safe_request(url, stream=True)
            with open(filename, 'wb') as file_out:
                for chunk in response.iter_content(chunk_size=4096):
                    file_out.write(chunk)
        except HTTPError as e:
            print("\nHTTP Error! Use a valid access token to give downloads!")
            print(e)
        except Exception as e:
            print(e)


def get_url_assets(items, tiles, bands, path_output):
    """Filter Asset URL addresses using json_path_rw extensions.

       :param items: Items selected based on datetime and Collection ID
       :type items: stac.item.ItemCollection
       :param tiles: Tile numbers related on grid of product. For example, Smart_Grid for Sentinel cubes.
       :type tiles: list
       :param bands: Band names or band common names (Ex.: B04 or red, in Sentinel cube).
       :type bands: list
       :param path_output: Path to download images and save patches
       :type path_output: str
       """
    assets_download = []
    for tile in tiles:
        member_has_tile = jp.match("features[?(properties.'bdc:tiles'[?(@~'{}')])]".format(tile), items)
        if not member_has_tile:
            raise IndexError("The collection doesn't have the tile: {}".format(tile))

        for member in member_has_tile:
            print("Feature id: {} has tile {}".format(member['id'], member['properties']['bdc:tiles']))
            if 'all' not in bands:
                for band in bands:
                    band_name = jp.match("properties.'eo:bands'[?common_name='" + band + "'].name", member)
                    if not band_name and band not in member['assets']:
                        raise IndexError("The STAC Item doesn't have an Asset with band name: {}".format(band))
                    else:
                        if band in member['assets']:
                            assets_download.extend([(path_output, member['assets'][band]['href'])])
                        else:
                            assets_download.extend([(path_output, member['assets'][band_name[0]]['href'])])
            else:
                assets_download.extend([(path_output, asset[1]['href']) for asset in member['assets'].items()])
    return assets_download


def divide_chunks(l_dimension, n):
    """Yield successive n-sized chunks from list of dimension.

       :param l_dimension: List of numbers until dimension
       :type l_dimension: list
       :param n: Size of chunks
       :type n: int
       """
    # looping till length l_dimension
    for i in range(0, len(l_dimension), n):
        yield l_dimension[i:i + n]


def rasterio_windows(totalwidth, totalheight, subwidth, subheight):
    """Create sequence of RasterIO windows to create patches.

       :param totalwidth: Width image size
       :type totalwidth: int
       :param totalheight: Height image size
       :type totalheight: int
       :param subwidth: Width patch image size
       :type subwidth: int
       :param subheight: Height patch image size
       :type subheight: int
       """
    w_n = list(divide_chunks(list(range(totalwidth)), subwidth))
    h_n = list(divide_chunks(list(range(totalheight)), subheight))
    wins = [rasterio.windows.Window(w[0], h[0], len(w), len(h)) for h in h_n for w in w_n]
    return wins


def process(window):
    """Create patches images using RasterIO with concurrency.

       :param window: Path to save image, spatial information of patch, RasterIO dataset reader object, thread lock
                      and RasterIO window parameters.
       :type window: tuple
    """
    outfile, kwargs, src, read_lock, window = window

    if not os.path.exists(outfile):
        try:
            with read_lock:
                # if no data in window, skip processing the window
                if not src.read_masks(1, window=window).any():
                    return
                src_array = src.read(window=window)
                win_array = rasterio.windows.Window(0, 0, src_array.shape[2], src_array.shape[1])
                kwargs.update({'transform': rasterio.windows.transform(window, src.transform)})

            with rasterio.open(outfile, "w", **kwargs) as dest:
                dest.write(src_array, window=win_array)
        except Exception as e:
            print(e)


def run_with_retry(func: callable, max_retries: int = 3, wait_seconds: int = 2, **func_params):
    """Execute functions with retry, especially to handle HTTP errors.

       :param func: Function to run
       :type func: function
       :param max_retries: Number of retryFunction to run
       :type max_retries: int
       :param wait_seconds: Seconds to wait until the new retry
       :type func: int
       """
    num_retries = 1
    while True:
        try:
            return func(*func_params.values())
        except Exception as e:
            if num_retries > max_retries:
                print('We have reached maximum errors and raising the exception')
                raise e
            else:
                print(f'{num_retries}/{max_retries}')
                print("Retrying error:", e)
                num_retries += 1
                sleep(wait_seconds)


def _url_open(url):
    """Read URL address using urllib.request module.

       :param url: URL for the Asset
       :type url: str
       """
    return urlopen(url).read()

class PatchBuilder:
    """Define Patch Builder interface for patches images creation."""

    def __init__(self, url, collection_id, tiles, datetime, bands, size, access_token=None, **request_kwargs):
        """Create a STAC client attached to the given host address (an URL).

           :param url: URL for the Root STAC Catalog.
           :type url: str
           :param collection_id: A string for a given collection_id.
           :type collection_id: str
           :param tiles: A string list with grid tiles.
           :type tiles: str
           :param datetime: 'Single date, date+time, or range (\'/\' separator), formatted to RFC 3339,
                             section 5.6'
           :type datetime: str
           :param bands: A string list of Assets.
           :type bands: str
           :param size: Patch dimension in pixels (height x width).
           :type size: str
           :param access_token: Authentication for the STAC API
           :type access_token: str
           """
        self._url = url
        self._access_token = access_token
        self._collection_id = collection_id
        self._tiles = tiles.split(',')
        self._datetime = datetime
        self._bands = bands.split(',')
        self._hsize, self._wsize = [int(value) for value in size.split('x')]
        self._collection_id = collection_id
        self._request_kwargs = request_kwargs

    def list_items(self):
        """Retrieve all Assets from a Collection based on datetime, Collection ID, tile and bands name

        :returns: A tuple with the raw path to downloaded images and URL to Asset.
        :rtype: tuple
        """
        service = stac.STAC(self._url, access_token=self._access_token)
        items = service.search({'collections': [self._collection_id], 'datetime': self._datetime, 'limit': 1})
        if not items['features']:
            raise ValueError('Items matched: {}'.format(items['context']['matched']))
        matched_items = items['context']['matched']
        items = service.search({'collections': [self._collection_id], 'datetime': self._datetime,
                                'limit': matched_items})
        retrived_items = jp.match1("$.features.`len`", items)
        if retrived_items != matched_items:
            raise ValueError('Items matched: {}  is different from the number of items retrieved:{}'.format(
                matched_items, retrived_items))
        else:
            assets_downloads = get_url_assets(items, self._tiles, self._bands, self._request_kwargs['path_output'])

        return assets_downloads

    def download_items(self):
        """Retrieve and download all Assets from a Collection based on datetime, Collection ID, tile and bands name

        :returns: A tuple with the raw path to downloaded images and URL to Asset.
        :rtype: tuple
        """
        service = stac.STAC(self._url, access_token=self._access_token)
        items = service.search({'collections': [self._collection_id], 'datetime': self._datetime, 'limit': 1})
        if not items['features']:
            raise ValueError('Items matched: {}'.format(items['context']['matched']))
        matched_items = items['context']['matched']
        items = service.search({'collections': [self._collection_id], 'datetime': self._datetime,
                                'limit': matched_items})
        retrived_items = jp.match1("$.features.`len`", items)
        if retrived_items != matched_items:
            raise ValueError('Items matched: {}  is different from the number of items retrieved:{}'.format(
                matched_items, retrived_items))
        else:
            assets_downloads = get_url_assets(items, self._tiles, self._bands, self._request_kwargs['path_output'])
            os.makedirs(self._request_kwargs['path_output'], exist_ok=True)
            print('Creating pool with %d ThreadPoolExecutor to download files\n' % num_workers)
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                executor.map(url_response, assets_downloads)

        return assets_downloads

    def patch_items(self, items):
        """Retrieve and download all Assets from a Collection based on datetime, Collection ID, tile and bands name

           :param items: A tuple with path to save patches and URL to Assets retrieved
           :type items: tuple
           """

        for path_out,url in items:
            filename = os.path.join(path_out, urlparse(url)[2].split('/')[-1])
            dirname = '_'.join(os.path.basename(filename).split('_')[:-1])
            target_dir = os.path.join(os.path.dirname(filename),dirname)
            os.makedirs(target_dir, exist_ok=True)

            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    tif_bytes = f.read()
            else:
                tif_bytes = run_with_retry(func=_url_open, param1=url)

            with rasterio.io.MemoryFile(tif_bytes) as memfile:
                with memfile.open() as src:
                    # Process the windows concurrently.
                    prefix, ext = os.path.splitext(os.path.basename(filename))
                    base_out = os.path.join(target_dir,prefix)

                    kwargs = src.meta.copy()
                    kwargs.update({'height': self._hsize,
                                   'width': self._wsize})
                    """We cannot write or read to the same file from multiple threads without causing race conditions.
                        To safely read from multiple threads, we use a lock to protect the DatasetReader/Writer"""
                    read_lock = threading.Lock()

                    windows = [(base_out + '_' + str(count) + ext, kwargs, src, read_lock, window)
                               for count, window in enumerate(rasterio_windows(src.width, src.height, self._wsize,
                                                                               self._hsize))]
                    start = timeit.default_timer()
                    # We map the process() function over the list of windows.
                    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                        executor.map(process, windows)
                    print('Time elapsed (sec):', timeit.default_timer() - start)






