from .grafts import graft, Graft, Namespace
from .formatters import mark
from .logical import Logical
from .targeting import Target
from .user_data import UserFacts

__all__ = ['graft', 'Graft', 'Logical', 'mark', 'Namespace', 'Target',
           'UserFacts']
__version__ = '0.4'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
