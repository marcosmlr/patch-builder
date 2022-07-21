..
    This file is part of Python Library for Patches Creator.
    Copyright (C) 2021 INPE.

    Python Library for Patches Creator is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Changes
=======

Version 0.2.0 (2022-07-20)
-------------

- Command Line Interface (CLI) program adapted for debugging.

- Changed parallel processing with lock (RasterIO) to concurrently processing using GDAL memory file.

- Determine the ideal number of threads based on CPU hardware (limited to 90% of cores).

- Include a command option to CLI to process files from the cloud or locally.

- Include installation instructions for GDAL on Python Virtual Environment.


Version 0.1.0 (2022-07-11)
-------------

- Command Line Interface (CLI).

- Documentation system based on Sphinx.

- Installation and build instructions.

- Package support through Setuptools.

- Installation and usage instructions.

- Source code versioning based on `Semantic Versioning 2.0.0 <https://semver.org/>`_.

- License: `MIT <https://github.com/brazil-data-cube/patch-builder/blob/master/LICENSE>`_.
