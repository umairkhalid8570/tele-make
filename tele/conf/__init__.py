# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

""" Library-wide configuration variables.

For now, configuration code is in tele.tools.config. It is in mainly
unprocessed form, e.g. applets_path is a string with commas-separated
paths. The aim is to have code related to configuration (command line
parsing, configuration file loading and saving, ...) in this module
and provide real Python variables, e.g. applets_paths is really a list
of paths.

To initialize properly this module, tele.tools.config.parse_config()
must be used.

"""

# Paths to search for tele applets.
applets_paths = []

# List of server-wide modules to load. Those modules are supposed to provide
# features not necessarily tied to a particular database. This is in contrast
# to modules that are always bound to a specific database when they are
# installed (i.e. the majority of tele applets). This is set with the --load
# command-line option.
server_wide_modules = []
