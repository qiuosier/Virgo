"""
This module uses scholar.py by Christian Kreibich
https://github.com/ckreibich/scholar.py

"""

import os
from Aries import web

scholar_path = os.path.join(os.path.dirname(__file__), "scholar.py")
if not os.path.exists(scholar_path):
    web.download(
        "https://raw.githubusercontent.com/ckreibich/scholar.py/master/scholar.py",
        scholar_path
    )


class GoogleScholar:
    pass