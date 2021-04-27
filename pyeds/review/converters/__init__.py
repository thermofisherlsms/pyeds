#  Created by Martin Strohalm, Thermo Fisher Scientific

# load main objects
from .converter import CONVERTERS, register, StringValueConverter, ImageValueConverter
from .common import NumberConverter, DDMapConverter, EnumConverter, StatusEnumConverter

# register specific converters
from . import cd_specific
from . import pd_specific
from . import trace
from . import spectrum

# try import plotting
try: from . import plotting
except ImportError: pass
