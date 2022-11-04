# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

""" Applets module.

This module serves to contain all Tele applets, across all configured applets
paths. For the code to manage those applets, see tele.modules.

Applets are made available under `tele.applets` after
tele.tools.config.parse_config() is called (so that the applets paths are
known).

This module also conveniently reexports some symbols from tele.modules.
Importing them from here is deprecated.

"""
# make tele.applets a namespace package, while keeping this __init__.py
# present, for python 2 compatibility
# https://packaging.python.org/guides/packaging-namespace-packages/
import pkgutil
import os.path
__path__ = [
    os.path.abspath(path)
    for path in pkgutil.extend_path(__path__, __name__)
]
