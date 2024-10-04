"""Temporary package to load functions for plotting, waiting for
the implementation in package `braun` accessible everywhere.

Also loads local modules whose data should be imported in a more robust way,
e.g. JSON, which is not implemented in package `braun` yet.
"""

import braun.utils.settings

settings = braun.utils.settings.import_module("settings")
thesis = braun.utils.settings.import_module("thesis")
plots = braun.utils.settings.import_module("plots")  # Must go last.
