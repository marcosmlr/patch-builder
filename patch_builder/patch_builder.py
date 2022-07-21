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
from osgeo import gdal
import numpy as np
import timeit
from time import sleep

gdal.UseExceptions()  # this allows GDAL to throw Python Exceptions
num_workers = int(cpu_count() - (cpu_count() * 0.10)) # using about 90% of cores


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


def patch_windows(totalWidth,totalHeight,subWidth,subHeight):
    """Create sequence of windows to build patches.

       :param totalwidth: Width image size
       :type totalwidth: int
       :param totalheight: Height image size
       :type totalheight: int
       :param subwidth: Width patch image size
       :type subwidth: int
       :param subheight: Height patch image size
       :type subheight: int
       """
    w_n=list(divide_chunks(list(range(totalWidth)), subWidth))
    h_n=list(divide_chunks(list(range(totalHeight)), subHeight))
    wins=[(w[0],h[0],len(w),len(h)) for h in h_n for w in w_n]
    return wins


def pixel_world(geoMatrix, x, y):
    """Calculate geographic coordinates of a pixel based on the raster projection and NumPy array indices.

       :param geoMatrix: Object containing affine transformation info for the raster
       :type geoMatrix: list
       :param x: Array column index for the upper left corner from the patch image
       :type x: int
       :param y: Array row index for the upper left corner from the patch image
       :type x: int

       Notes
       -----
       Uses the GDAL affine transformation (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation and y_size) to
       calculate the geospatial coordinate of a pixel location. The geomatrix object (gdal.GetGeoTransform()) contains
       the coordinates (in some projection) of the upper left (UL) corner of the image (taken to be the borders of the
       pixel in the UL corner, not the center), the pixel spacing and an additional rotation.
       """
    x_coord = geoMatrix[0] + (x * geoMatrix[1])
    y_coord = geoMatrix[3] + (y * geoMatrix[5])

    return x_coord, y_coord


#Adapted from https://here.isnew.info/how-to-save-a-numpy-array-as-a-geotiff-file-using-gdal.html
def write_geotiff(filename, arr, in_ds, w_index_x, w_index_y):
    """Write a patch image as a projected GeoTIFF file with GDAL based on the NumPy array.

       :param filename: Path to save image.
       :type filename: str
       :param arr: Window array values of patch.
       :type arr: numpy.ndarray
       :param in_ds: GDAL dataset object contains all information about the original raster (projection,
                     affine transformation, etc).
       :type in_ds: osgeo.gdal.Dataset
       :param w_index_x: Array column index for the upper left corner from the patch image.
       :type w_index_x: int
       :param w_index_y: Array row index for the upper left corner from the patch image.
       :type w_index_y: int
       """
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(filename, arr.shape[1], arr.shape[0], 1, in_ds.GetRasterBand(1).DataType)
    out_ds.SetProjection(in_ds.GetProjection())

    outGeoTransform = list(in_ds.GetGeoTransform())
    ul_coord_x, ul_coord_y = pixel_world(outGeoTransform, w_index_x, w_index_y)
    outGeoTransform[0] = ul_coord_x
    outGeoTransform[3] = ul_coord_y
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())
    out_ds.SetGeoTransform(tuple(outGeoTransform))
    band = out_ds.GetRasterBand(1)
    band.WriteArray(arr)
    band.SetNoDataValue(in_ds.GetRasterBand(1).GetNoDataValue())
    band.FlushCache()


def process(window_in):
    """Create patches images using GDAL with concurrency.

           :param window_in: Path to save image, patch rows, patch collums, nodata value, gdal dataset object
                             and window index parameters.
           :type window_in: tuple
        """
    outfile, rows_w, cols_w, nodata, in_ds, window = window_in

    if not os.path.exists(outfile):
        try:
            src_array = np.ones((rows_w, cols_w)) * nodata
            src_array[0: window[3], 0:window[2]] = in_ds.ReadAsArray(xoff=window[0], yoff=window[1],
                                                                     xsize=window[2], ysize=window[3])
            write_geotiff(outfile, src_array, in_ds, window[0], window[1])
        except Exception as e:
            print(e)


def run_with_retry(func: callable, max_retries: int = 3, wait_seconds: int = 2, **func_params):
    """Execute functions with retry, especially to handle HTTP errors.

       :param func: Function to run.
       :type func: function
       :param max_retries: Number of retryFunction to run.
       :type max_retries: int
       :param wait_seconds: Seconds to wait until the new retry.
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

       :param url: URL for the Asset.
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

            try:
                # Read a bytes stream through a virtual memory file
                vsipath = '/vsimem/'+os.path.basename(filename)
                gdal.FileFromMemBuffer(vsipath, tif_bytes)

                # create Memory driver
                ds = gdal.GetDriverByName('MEM').CreateCopy(
                    vsipath,
                    gdal.Open(vsipath))

            except RuntimeError as e:
                ds = None
                print("Unable to open " + filename)
                print(e)

            if ds != None:
                # Process the windows concurrently.
                prefix, ext = os.path.splitext(os.path.basename(filename))
                base_out = os.path.join(target_dir, prefix)

                # Get no data value of array
                noDataValue = ds.GetRasterBand(1).GetNoDataValue()
                if noDataValue == None:
                    noDataValue = 0

                windows = [(base_out + '_' + str(count) + ext, self._hsize, self._wsize, noDataValue, ds, window) for count, window
                           in enumerate(patch_windows(ds.RasterXSize, ds.RasterYSize, self._wsize, self._hsize))]

                start = timeit.default_timer()
                # We map the process() function over the list of windows.
                with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                    executor.map(process, windows)
                print('Time elapsed for patches creation (sec):', timeit.default_timer() - start)

            ds = None
            gdal.Unlink(vsipath)  # Free memory associated with the in-memory file
