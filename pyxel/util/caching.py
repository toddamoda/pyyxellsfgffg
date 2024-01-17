#  Copyright (c) European Space Agency, 2017.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Function(s) to get a global caching mechanism."""

import tempfile
from typing import Optional

from diskcache import Cache

_global_cache: Optional[Cache] = None


def get_cache(folder: Optional[str] = None) -> Cache:
    """Retrieve a global cache instance."""
    global _global_cache

    if _global_cache is None:
        if folder is None:
            folder = tempfile.gettempdir()

        _global_cache = Cache(directory=folder)

    return _global_cache
