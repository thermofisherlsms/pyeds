#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import os
import os.path
import tempfile
import uuid
from xml.sax.saxutils import escape
from .converter import register, StringValueConverter, ImageValueConverter
from .common import NumberConverter, DDMapConverter, StatusEnumConverter
from .utils import interpolate_color, rgba_to_hex


@register("20E15B78-40DF-48CA-9EFF-01FF2EBDCEDB")
class AnnotationStatusEnumConverter(StatusEnumConverter):
    """Converts enum into colorized status rectangle."""
    
    COLORS = {
        0: (0, 0, 0, 255),  # Unknown status
        1: (200, 200, 200, 255),  # No results
        2: (255, 50, 50, 255),  # No match
        3: (255, 175, 50, 255),  # Partial match
        4: (50, 200, 50, 255),  # Full match
        5: (255, 50, 50, 255),  # Invalid mass
        6: (255, 175, 50, 255),  # Unused
        7: (255, 175, 50, 255),  # Not the top hit
    }


@register("BB2BB091-2509-40DF-9632-40F68F421199")
class MSnStatusEnumConverter(StatusEnumConverter):
    """Converts enum into colorized status rectangle."""
    
    COLORS = {
        0: (255, 50, 50, 255),  # No MS2
        1: (50, 200, 50, 255),  # ddMS2 for preferred ion
        2: (100, 100, 255, 255),  # ddMS2 for other ion
        3: (255, 175, 50, 255),  # AIF only
    }


@register("4B72AF5C-3411-462F-83AE-70CA70D32C12")
class LabelingStatusEnumConverter(StatusEnumConverter):
    """Converts enum into colorized status rectangle."""
    
    COLORS = {
        0: (200, 200, 200, 255),  # Unknown status
        1: (200, 200, 200, 255),  # Not detected
        2: (50, 200, 50, 255),  # No warnings
        3: (255, 50, 50, 255),  # Contaminating mass
        4: (255, 175, 50, 255),  # Low pattern fit
        5: (255, 175, 50, 255),  # Irregular exchange
    }


@register("5BC9FD49-BE5D-41AE-A43C-78A9CE9436C4")
class GapFillStatusEnumConverter(StatusEnumConverter):
    """Converts enum into colorized status rectangle."""
    
    COLORS = {
        0: (50, 200, 50, 255),  # Unknown status
        1: (50, 200, 50, 255),  # No gap to fill
        2: (255, 50, 50, 255),  # Unable to fill
        4: (255, 175, 50, 255),  # Filled by arbitrary value
        8: (100, 100, 255, 255),  # Filled by trace area
        16: (100, 100, 255, 255),  # Filled by simulated peak
        32: (100, 100, 255, 255),  # Filled by spectrum noise
        64: (50, 200, 50, 255),  # Filled by matching ion
        128: (50, 200, 50, 255),  # Filled by re-detected peak
        256: (255, 175, 50, 255),  # Imputed by low area value
        512: (255, 175, 50, 255),  # Imputed by group median
        1024: (255, 175, 50, 255),  # Imputed by Random Forest
        2048: (255, 50, 50, 255),  # Skipped
        4096: (255, 200, 50, 255),  # Filled by re-used peak
        8192: (255, 200, 50, 255)  # Filled by unused peak
    }


@register("C922DE5A-9589-4021-B009-3C83D52030BD")
class GapFillStatusDDMapConverter(DDMapConverter):
    """Converts value into status distribution map."""
    
    TABLE_CLASS = "nopadding ddstatus"
    
    DISPLAY_NAMES = {
        0: "Unknown status",
        1: "No gap to fill",
        2: "Unable to fill",
        4: "Filled by arbitrary value",
        8: "Filled by trace area",
        16: "Filled by simulated peak",
        32: "Filled by spectrum noise",
        64: "Filled by matching ion",
        128: "Filled by re-detected peak",
        256: "Imputed by low area value",
        512: "Imputed by group median",
        1024: "Imputed by Random Forest",
        2048: "Skipped",
        4096: "Filled by re-used peak",
        8192: "Filled by unused peak"
    }
    
    LEVELS = {
        0: 1,
        1: 64 | 128 | 4096 | 8192,
        2: 8 | 16 | 32,
        3: 4 | 256 | 512 | 1024,
        4: 2 | 2048
    }
    
    COLORS = {
        0: (50, 200, 50, 255),
        1: (50, 200, 50, 255),
        2: (100, 100, 255, 255),
        3: (255, 175, 50, 255),
        4: (255, 50, 50, 255)
    }
    
    def GetBoxValue(self, prop, index):
        """Gets box value as it should be displayed."""
        
        # check data
        if prop.Value is None:
            return self.DISPLAY_NAMES[1]
        
        # get value
        value = prop.Value[index]
        if value == 0 or value is None:
            return self.DISPLAY_NAMES[1]
        
        # make labels
        labels = []
        for key in sorted(self.DISPLAY_NAMES):
            if key != 0 and (key & value) == key:
                labels.append(self.DISPLAY_NAMES[key])
        
        # make final label
        return "\n".join(labels)
    
    
    def GetBoxColor(self, prop, index):
        """Gets CSS color for specific value."""
        
        # check data
        if prop.Value is None:
            return self.COLORS[0]
        
        # get value
        value = prop.Value[index]
        if value == 0 or value is None:
            return self.COLORS[0]
        
        # get color
        for key in (4, 3, 2, 1, 0):
            if value & self.LEVELS[key] != 0:
                return self.COLORS[key]
        
        return self.COLORS[0]


@register("9ACA6BD7-EB95-4F7D-A293-F18EC06D10CF")
@register("6F0A4113-E338-454B-8E89-95C1BCE1380F")
class MOLStructureConverter(ImageValueConverter):
    """Converts MOL structure into SVG image."""
    
    IMAGE_FORMAT = 'svg'
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts MOL structure into SVG image.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            image: str or None
                SVG image data.
        """
        
        # check value
        if not prop.Value:
            return None
        
        # try to convert into RDKit object
        try:
            from rdkit.Chem import AllChem
            from rdkit.Chem import Draw
            mol = AllChem.MolFromMolBlock(prop.Value)
        except ImportError:
            return None
        
        # get image path
        filename = "%s.%s" % (str(uuid.uuid4()), "svg")
        path = os.path.join(tempfile.gettempdir(), filename)
        
        # set drawing options
        options = Draw.MolDrawOptions()
        options.baseFontSize = 0.5
        options.bondLineWidth = 1
        
        # make image
        Draw.MolToFile(mol, path, size=(120, 75), options=options, fitImage=False, ignoreHs=True)
        
        # read image data
        with open(path) as svg_file:
            svg = svg_file.read()
        
        # delete file
        os.remove(path)
        
        return svg


@register("ResultItemDataPurpose/ElementalCompositionFormula")
class ElementalCompositionConverter(StringValueConverter):
    """Converts elemental composition formula."""
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts elemental composition formula.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            output: str
                Formatted formula.
        """
        
        # check value
        if prop.Value is None:
            return ""
        
        # remove spaces
        formula = prop.Value.replace(" ", "&nbsp;")
        
        # use subscript
        # formula = re.sub(r"(\d+)",  r"<sub>\1</sub>", formula)
        
        return formula


@register("DeltaMass")
class DeltaMassConverter(NumberConverter):
    """Converts mass error to background color."""
    
    THRESHOLD = 0.5
    
    
    def GetCellStyle(self, prop):
        """
        Gets specific cell CSS style based on given value.
        
        Args:
            prop: pyeds.PropertyValue
                Property to use.
        
        Returns:
            str or None
                CSS style or None for default.
        """
        
        # check threshold
        if prop.Value and abs(prop.Value) > self.THRESHOLD:
            return 'background-color:#ffaf32"'
        
        # no warning
        return None


@register("D1F4F750-776D-411D-B7D0-D6206ECDBE91")
@register("ResultItemDataPurpose/DeltaMassInDa")
class DeltaMassDaConverter(DeltaMassConverter):
    """Converts mass error (in Da) to background color."""
    
    THRESHOLD = 0.5


@register("29A89690-0776-4514-8A25-F03309B31FD4")
@register("ResultItemDataPurpose/DeltaMassInPPM")
class DeltaMassPpmConverter(DeltaMassConverter):
    """Converts mass error (in ppm) to background color."""
    
    THRESHOLD = 5


@register("WebLink")
class WebLinkConverter(StringValueConverter):
    """Converts value into active web link."""
    
    URL = ""
    
    def Convert(self, prop, **kwargs):
        """
        Converts value into active web link.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            output: str
                Formatted web link.
        """
        
        # check value
        if not prop.Value:
            return ""
        
        # get values for URL
        values = self.GetUrlValues(prop)
        if not values:
            return ""
        
        # make URL
        url = self.URL % tuple(values)
        
        # make link
        return '<a href="%s" title="Open web link">%s</a>' % (url, escape(str(prop.Value)))
    
    
    def GetUrlValues(self, prop):
        """Provides url."""
        
        return (escape(str(prop.Value)),)


@register("049EF53F-DE02-422F-B051-F0678E03832B")
class MzCloud1WebLinkConverter(WebLinkConverter):
    """Converts value into active web link."""
    
    URL = "https://mzcloud.org/DataViewer.Aspx#C%s%s"
    
    
    def GetUrlValues(self, prop):
        """Provides url."""
        
        return prop.Value.split('-')


@register("8324856E-E547-4ED1-B344-56DDDE8B0F7B")
class MzCloud2WebLinkConverter(WebLinkConverter):
    """Converts value into active web link."""
    
    URL = "https://mzcloud2.cmdstage.thermofisher.com/DataViewer/app/dataviewer/library/%s?query=myCloudId=%s"
    
    
    def GetUrlValues(self, prop):
        """Provides url."""
        
        return prop.Value.split('/')


@register("4D9457A0-818E-4A26-A2C1-6DD46B2300EF")
class ChemSpiderWebLinkConverter(WebLinkConverter):
    """Converts value into active web link."""
    
    URL = "http://www.chemspider.com/%s"


@register("CA98CFAC-310A-4C09-8CC6-5D39AD44402A")
class KEGGWebLinkConverter(WebLinkConverter):
    """Converts value into active web link."""
    
    URL = "http://www.genome.jp/dbget-bin/www_bget?%s"


@register("6C8927E9-54F0-4C6D-BA36-6B2DC172A961")
class HMDBWebLinkConverter(WebLinkConverter):
    """Converts value into active web link."""
    
    URL = "https://www.hmdb.ca/metabolites/%s"


@register("EEC52B62-E475-4FD5-9BE1-BCC40C5436DD")
@register("C0699364-5E3A-41C9-9F27-690A41CC2385")
class PubChemWebLinkConverter(WebLinkConverter):
    """Converts value into active web link."""
    
    URL = "https://pubchem.ncbi.nlm.nih.gov/compound/%s"


@register("E20AA096-5B91-40AE-A85F-562C29816869")
class IsolationPurityConverter(NumberConverter):
    """Converts isolation purity to background color."""
    
    GOOD_COLOR = (50, 205, 50, 255)
    BAD_COLOR = (255, 175, 50, 255)
    THRESHOLD = 50
    
    
    def GetCellStyle(self, prop):
        """
        Gets specific cell CSS style based on given value.
        
        Args:
            prop: pyeds.PropertyValue
                Property to use.
        
        Returns:
            str or None
                CSS style or None for default.
        """
        
        # check value
        if prop.Value is None:
            return None
        
        # below threshold
        if prop.Value < self.THRESHOLD:
            return self.BAD_COLOR
        
        # get gradient color
        pos = (prop.Value - self.THRESHOLD) / (100 - self.THRESHOLD)
        color = interpolate_color(self.BAD_COLOR, self.GOOD_COLOR, pos)
        
        return 'background-color:%s"' % rgba_to_hex(color)


@register("F62B4AA7-94C2-41BB-B759-F6F99BEA299A")
class PeakRatingConverter(NumberConverter):
    """Converts peak rating to background color."""
    
    LEVELS = (0.0, 2.5, 5.0, 7.5, 10.0)
    
    COLORS = (
        (255, 0, 0, 255),
        (255, 175, 50, 255),
        (255, 255, 0, 255),
        (173, 255, 47, 255),
        (50, 205, 50, 255))
    
    
    def GetCellStyle(self, prop):
        """
        Gets specific cell CSS style based on given value.
        
        Args:
            prop: pyeds.PropertyValue
                Property to use.
        
        Returns:
            str or None
                CSS style or None for default.
        """
        
        # check value
        if prop.Value is None:
            return None
        
        # init color
        color = self.COLORS[-1]
        
        # below threshold
        for i, threshold in enumerate(self.LEVELS):
            if prop.Value < threshold:
                color = self.COLORS[i]
                break
        
        return 'background-color:%s"' % rgba_to_hex(color)
