#  Created by Martin Strohalm, Thermo Fisher Scientific

# init main repository
CONVERTERS = {}


def register(tag):
    """Registers converter by given tag."""
    
    def reg(cls):
        """Registers given class."""
        
        CONVERTERS[tag] = cls
        CONVERTERS[tag.lower()] = cls
        CONVERTERS[tag.upper()] = cls
        
        return cls
    
    return reg


class ValueConverter(object):
    """
    The pyeds.report.ValueConverter class provides a base for all property value
    converters. These converters are automatically used by the review module to
    convert property values into final review representation. The selection of
    particular converter is realized via 'GridCellControlGuid', DataPurpose,
    'SpecialValueTypeName' or 'CustomDataType.Name'.
    
    You can create your custom converters by creating derived class from the
    'pyeds.review.StringValueConverter' or 'pyeds.review.ImageValueConverter'
    and registering it by 'pyeds.review.register' decorator using appropriate
    GridCellControlGuid, DataPurpose, SpecialValueTypeName, DataType.Name or
    CustomDataType.Name.
    """

    CELL_CLASS = None
    CELL_STYLE = None
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts property value.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            ?
                Converted property value.
        """
        
        raise NotImplementedError()
    
    
    def GetCellClass(self, prop):
        """
        Gets specific cell CSS class based on given value.
        
        Args:
            prop: pyeds.PropertyValue
                Property to use.
        
        Returns:
            str or None
                Classes or None for default.
        """
        
        return self.CELL_CLASS
    
    
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
        
        return self.CELL_STYLE


class StringValueConverter(ValueConverter):
    """
    The pyeds.StringValueConverter class provides a base for those property
    value converters where the conversion output is the final HTML to be
    inserted into review.
    """
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts property value into HTML to be inserted into review.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            str
                Final HTML.
        """
        
        raise NotImplementedError()


class ImageValueConverter(ValueConverter):
    """
    The pyeds.ImageValueConverter class provides a base for those property value
    converters where the conversion output is an image to be inserted into
    review. For SVG the output is expected as full SVG XML, for binary images
    the binary data. Converted value will be stored in a file linked to
    generated review. For derived classes, please specify the 'IMAGE_FORMAT'
    attribute, which will be used as the file extension to store the image file.
    """
    
    IMAGE_FORMAT = 'svg'
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts property value into image data to be inserted into review.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            str or binary
                Image data.
        """
        
        raise NotImplementedError()
