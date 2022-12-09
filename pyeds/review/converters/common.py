#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import numpy
from xml.sax.saxutils import escape
from ..helpers import *
from .converter import register, StringValueConverter


@register("ResultItemDataPurpose/CheckState")
class CheckStateConverter(StringValueConverter):
    """The pyeds.CheckStateConverter class converts checked state."""
    
    CELL_CLASS = "nopadding center"
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts checked state into string.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            str
                Checked state.
        """
        
        title = 'True' if prop.Value else 'False'
        char = '&#x2713;' if prop.Value else '&nbsp;'
        
        return '<span title="%s" class="checked">%s</span>' % (title, char)


@register("6B12C108-48D6-420A-BA95-B57BA1EFD7D1")
class TagsConverter(StringValueConverter):
    """
    The pyeds.TagsConverter class converts data distribution map of custom tags.
    """
    
    CELL_CLASS = "nopadding center"
    NONE_COLOR = (230, 230, 230, 255)
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts custom tags.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            str
                Custom tags HTML.
        """
        
        # init HTML
        html = '<div class="tags">'
        
        # get ddmap
        ddmap = prop.Type.SpecialValueType
        
        # add tags
        for box in ddmap.Boxes:
            
            # skip hidden
            if box.ExtendedData.get('EntityItemTagVisibility', None) != 'True':
                continue
            
            # get values
            value = prop.Value[box.Index] if prop.Value is not None else None
            
            # get color
            color = rgba_from_argb_int(box.Color) if value else self.NONE_COLOR
            color = "rgba(%s,%s,%s,%s);" % color
            
            # add to HTML
            html += '<span title="%s" style="color:%s">&#x25CF;</span>' % (box.Name, color)
        
        # finalize HTML
        html += '</div>'
        
        return html


@register("Int")
@register("Int64")
@register("Double")
class NumberConverter(StringValueConverter):
    """
    The pyeds.NumberConverter class converts number into string using defined
    formatting.
    """
    
    CELL_CLASS = "right"
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts number into string.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            str
                Formatted number.
        """
        
        # check value
        if prop.Value is None:
            return ""
        
        # apply formatting
        if prop.Type.FormatString:
            return format_float(prop.Value, prop.Type.FormatString)
        
        return str(prop.Value)


@register("38448540-6FA7-43CE-9B83-48383DDB282D")
@register("B8336E98-B9AF-4213-BF96-91D14FE44E99")
class NumberArrayConverter(StringValueConverter):
    """
    The pyeds.NumberArrayConverter class converts arrays of numbers into string
    representation similar to numpy print.
    """
    
    CELL_CLASS = "left"
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts array into string.

        Args:
            prop: pyeds.PropertyValue
                Property to convert.

        Returns:
            str
                Formatted array.
        """
        
        # check value
        if prop.Value is None:
            return ""
        
        # convert to array
        return str(numpy.array(prop.Value))


@register("Enum")
class EnumConverter(StringValueConverter):
    """
    The pyeds.EnumConverter class serves as a generic converter for enums to
    show the 'DisplayName' instead of the real integer value.
    """
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts enum into its display name.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            str
                Enum value display name.
        """
        
        return self.GetValue(prop)
    
    
    def GetValue(self, prop):
        """Gets value as it should be displayed."""
        
        # check value
        if prop.Value is None:
            return ""
        
        # format value
        elements = [e.DisplayName or str(e) for e in prop.Value.Elements]
        return "|".join(elements)
    
    
    def GetTooltip(self, prop):
        """Gets box tooltip."""
        
        # check value
        if prop.Value is None:
            return ""
        
        # format value
        elements = [e.DisplayName or str(e) for e in prop.Value.Elements]
        return "\n".join(elements)


@register("StatusEnum")
class StatusEnumConverter(EnumConverter):
    """
    The pyeds.StatusEnumConverter class provide a base to convert enums into
    colorized status rectangle. Any derived class is expected to overwrite the
    'COLORS' dictionary to provide correct color for individual enum values.
    """
    
    COLORS = {}
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts enum into status rectangle.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            str
                Status enum HTML.
        """
        
        # check value
        if prop.Value is None:
            return ""
        
        # get value
        value = self.GetValue(prop)
        
        # get tooltip
        tooltip = self.GetTooltip(prop)
        
        # get color
        color = self.GetColor(prop)
        
        # set style
        style = ""
        if color:
            color = trans_color(color, alpha=.75)
            style = "background-color: rgba(%s,%s,%s,%s);" % color
        
        # make HTML
        return "<div title=\"%s\" class=\"enumstat\" style=\"%s\">%s</div>" % (tooltip, style, value)
    
    
    def GetColor(self, prop):
        """Gets CSS color for specific value."""
        
        return self.COLORS.get(prop.Value.Value, None)


@register("DataDistribution")
class DDMapConverter(StringValueConverter):
    """
    The pyeds.DDMapConverter class serves as generic converter of data
    distribution maps into a heat-map-like table containing all values.
    """
    
    CELL_CLASS = "nopadding center"
    TABLE_CLASS = ""
    NONE_COLOR = (200, 200, 200, 255)
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts data distribution map into mini table.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            str
                Map values table HTML.
        """
        
        # init HTML
        html = "<table class=\"ddmap %s\"><tr>" % self.TABLE_CLASS
        
        # get ddmap
        ddmap = prop.Type.SpecialValueType
        
        # format values
        for index in range(len(ddmap.Boxes)):
            
            # get value
            value = self.GetBoxValue(prop, index)
            
            # check value
            if value is None:
                value = "&nbsp;"
            
            # get tooltip
            tooltip = self.GetBoxTooltip(prop, index)
            
            # mark group start
            cls = ""
            if ddmap.GetBox(index).IsFirstInGroup and index != 0:
                cls += "ddgroup"
            
            # get style
            style = self.GetBoxStyle(prop, index)
            
            # add to HTML
            html += "<td title=\"%s\" class=\"%s\" style=\"%s\">%s</td>" % (tooltip, cls, style, value)
        
        # finalize HTML
        html += "</tr></table>"
        
        return html
    
    
    def GetBoxValue(self, prop, index):
        """Gets box value as it should be displayed."""
        
        # check data
        if prop.Value is None:
            return None
        
        # get value
        value = prop.Value[index]
        if value is None:
            return None
        
        # format float
        if prop.Value.Type.CustomDataType.Name == "Double":
            formatting = prop.Type.FormatString
            value = format_float(value, formatting)
        
        return str(value)
    
    
    def GetBoxTooltip(self, prop, index):
        """Gets box tooltip."""
        
        status = self.GetBoxValue(prop, index)
        box = prop.Type.SpecialValueType.GetBox(index)
        
        return "%s\n@ %s" % (status, box.Name)
    
    
    def GetBoxStyle(self, prop, index):
        """Gets box CSS."""
        
        style = ""
        
        # set group start
        if prop.Type.SpecialValueType.GetBox(index).IsFirstInGroup and index:
            style += "border-left_width: 5pt;"
        
        # set alignments
        style += " text-align: right;"
        
        # set color
        color = self.GetBoxColor(prop, index)
        if color:
            color = trans_color(color, alpha=.75)
            style += " background-color: rgba(%s,%s,%s,%s);" % color
        
        return style
    
    
    def GetBoxColor(self, prop, index):
        """Gets CSS color for specific value."""
        
        # check data
        if prop.Value is None or prop.Value[index] is None:
            return self.NONE_COLOR
        
        # get data
        box = prop.Value.GetBox(index)
        level = prop.Value.GetLevel(index)
        
        # get color
        color = level.Color if level and level.Color else box.Color
        
        # convert to RGBA
        if color:
            color = rgba_from_argb_int(color)
        
        return color


@register("0E783F77-3B03-43CD-817E-E6FC1E0E2CB2")
class StatusDDMapConverter(DDMapConverter):
    """Converts value into status distribution map."""
    
    TABLE_CLASS = "nopadding ddstatus"
    
    
    def GetBoxValue(self, prop, index):
        """Gets box value as it should be displayed."""
        
        # check value
        if prop.Value is None:
            return None
        
        # get level
        value = prop.Value[index]
        level = prop.Value.GetLevel(index)
        
        # use level
        if level is not None and level.Description:
            return level.Description
        
        # use value
        return str(value)


@register("B4FF5180-00AE-42DC-8F5A-046B82CDAA19")
class OnOffDDMapConverter(DDMapConverter):
    """Converts value into ON/OFF distribution map."""
    
    TABLE_CLASS = "nopadding ddonoff"
    NONE_COLOR = (255, 255, 255, 255)
    
    
    def GetBoxValue(self, prop, index):
        """Gets box value as it should be displayed."""
        
        # check value
        if prop.Value is None:
            return None
        
        # get value
        value = prop.Value[index]
        return "True" if value else "False"


@register("Template")
class TemplateConverter(StringValueConverter):
    """
    The pyeds.TemplateConverter class converts values into string using defined
    template (e.g. '{:.2f}').
    """
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts value into string using Python formatting.

        Args:
            prop: pyeds.PropertyValue
                Property to convert.

        Returns:
            str
                Formatted value.
        """
        
        # check value
        if prop.Value is None:
            return ""
        
        # apply formatting
        if prop.Type.FormatString:
            return prop.Type.FormatString.format(prop.Value)
        
        return escape(str(prop.Value))


@register("ECF3E1A3-0A57-458E-8C9C-83B5B1476242")
@register("4B86C2D4-15AC-4E04-93A4-E05E35F72363")
class FileIDConverter(StringValueConverter):
    """Provides real file name as a tooltip for various file IDs."""
    
    
    def Convert(self, prop, **kwargs):
        """
        Converts value into value with file name tooltip.
        
        Args:
            prop: pyeds.PropertyValue
                Property to convert.
        
        Returns:
            str
                Formatted value.
        """
        
        # check value
        if prop.Value is None:
            return ""
        
        # init file names
        if '_names' not in locals():
            
            # init lookup
            self._names = {}
            
            # set names
            if self.EDS is not None:
                with self.EDS:
                    for item in self.EDS.Read("WorkflowInputFile"):
                        self._names[item.FileID] = item.FileName
                        self._names[item.StudyFileID] = item.FileName
        
        # get tooltip
        tooltip = self._names.get(prop.Value, "")
        
        # make HTML
        return "<div title=\"%s\" >%s</div>" % (tooltip, prop.Value)
