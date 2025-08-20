#  Created by Martin Strohalm, Thermo Fisher Scientific

# load main objects
from .converter import CONVERTERS, register, StringValueConverter, ImageValueConverter
from .common import NumberConverter, DDMapConverter, EnumConverter, StatusEnumConverter

# register specific converters
from . import cd_specific
from . import pd_specific
from . import trace
from . import spectrum

# import utils
from .utils import ICON_INFO, ICON_WARNING, ICON_ERROR, ICON_STOP
from .utils import interpolate_color, rgba_to_hex, make_icon

# try import plotting
try: from . import plotting
except ImportError: pass
