..
    This file is part of Python Library for Patches Creator.
    Copyright (C) 2021 INPE.

    Python Library for Patches Creator is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


==================================
Python Library for Patches Creator
==================================


.. image:: https://img.shields.io/badge/license-MIT-green
        :target: https://github.com//brazil-data-cube/patch-builder/blob/master/LICENSE
        :alt: Software License


.. image:: https://readthedocs.org/projects/patch_builder/badge/?version=latest
        :target: https://patch_builder.readthedocs.io/en/latest/
        :alt: Documentation Status


.. image:: https://img.shields.io/badge/lifecycle-maturing-blue.svg
        :target: https://www.tidyverse.org/lifecycle/#maturing
        :alt: Software Life Cycle


.. image:: https://img.shields.io/github/tag/brazil-data-cube/patch-builder.svg
        :target: https://github.com/brazil-data-cube/patch-builder/releases
        :alt: Release


.. image:: https://img.shields.io/discord/689541907621085198?logo=discord&logoColor=ffffff&color=7389D8
        :target: https://discord.com/channels/689541907621085198#
        :alt: Join us at Discord


About
=====


The state-of-the-art models for many image classification tasks are based on Convolutional Neural Networks (CNN). However, to map land use and land cover information based on training a CNN on a hole resolution of satellite images is actually computationally impossible. One way to avoid this is using a subset of images in patch scale, sometimes features observed on image patches can perform better than an image-level classifier.

The patch creator is a python package that provides a simple interface to access satellite images stack from the Brazil Data Cube (BDC) project aiming to permit build a set o patch images to support a large number of applications, including image classification and Content-Based Image Retrieval (CBIR) and captioning using Deep Learning Models.  The BDC project is part of the “Environmental Monitoring of Brazilian Biomes project“, funded by the Amazon Fund through the financial collaboration of the Brazilian Development Bank (BNDES) and the Foundation for Science, Technology and Space Applications (FUNCATE) no. 17.2.0536.1. Brazil Data Cube is the successor of the research project e-sensing, funded by FAPESP (Fapesp 2014/08398-6).
