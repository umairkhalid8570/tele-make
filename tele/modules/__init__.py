# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

""" Modules (also called applets) management.

"""

from . import db, graph, loading, migration, module, registry

from tele.modules.loading import load_modules, reset_modules_state

from tele.modules.module import (
    adapt_version,
    get_module_path,
    get_module_resource,
    get_modules,
    get_modules_with_version,
    get_resource_from_path,
    get_resource_path,
    check_resource_path,
    initialize_sys_path,
    load_information_from_description_file,
    load_telecms_module,
)
