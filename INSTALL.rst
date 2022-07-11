..
    This file is part of Python Library for Patches Creator.
    Copyright (C) 2021 INPE.

    Python Library for Patches Creator is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Installation
============

``patch-builder`` depends essentially on stac.py, json-path and RasterIO. Please, read the instructions below in order to install ``patch-builder``.

Production installation
-----------------------

**Under Development!**

Development Installation - GitHub
---------------------------------

Clone the Software Repository
+++++++++++++++++++++++++++++

Use ``git`` to clone the software repository:

.. code-block:: shell

        $ git clone https://github.com/marcosmlr/patch-builder.git

Install patch-builder in Development Mode
+++++++++++++++++++++++++++++++++++

Go to the source code folder:

.. code-block:: shell

        $ cd patch-builder

Install in development mode:

.. code-block:: shell

        $ pip3 install -e .[all]

.. note::

    If you want to create a new *Python Virtual Environment*, please, follow this instruction:

    *1.* Create a new virtual environment linked to Python 3.8::

        python3.8 -m venv venv


    **2.** Activate the new environment::

        source venv/bin/activate


    **3.** Update pip and setuptools::

        pip3 install --upgrade pip

        pip3 install --upgrade setuptools


Run the Tests
+++++++++++++

Run the tests:

.. code-block:: shell

        $ ./run-tests.sh


Build the Documentation
+++++++++++++++++++++++

Generate the documentation:

.. code-block:: shell

        $ python setup.py build_sphinx

The above command will generate the documentation in HTML and it will place it under:

.. code-block:: shell

    docs/sphinx/_build/html/

You can open the above documentation in your favorite browser, as:

.. code-block:: shell

    firefox docs/sphinx/_build/html/index.html
