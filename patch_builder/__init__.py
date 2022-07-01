#
# This file is part of Python Library for Patches Creator.
# Copyright (C) 2021 INPE.
#
# Python Library for Patches Creator is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Python Library for Patches Creator."""

from . import cli
from .patch_builder import PatchBuilder
from .version import __version__


__all__ = ('__version__',
           'PatchBuilder')
