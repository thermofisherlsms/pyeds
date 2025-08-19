#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import re
import os.path
import shutil
import uuid
import webbrowser
from xml.sax.saxutils import escape
from ..eds import EDS
from .converters import CONVERTERS, ImageValueConverter


GUID_PATTERN = re.compile("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class Review(object):
    """
    The pyeds.Review class provides a simple way of generating HTML reports from
    data retrieved by pyeds.EDS module. You can just insert multiple items at
    once or on-by-one or even a whole hierarchy. Those will automatically be
    converted into tables containing appropriate headers.
    
    Any property or even a whole entity item can be converted into a desired
    representation (e.g. special formatting or even an image representation) by
    registering appropriate converter. See the pyeds.review.ValueConverter for
    more information.
    """
    
    
    def __init__(self, eds=None, title="Review", folder="review_data", clear=True):
        """
        Initializes a new instance of Review.
        
        Args:
            eds: pyeds.EDS or None
                Instance of EDS. If not provided, some converters may not work
                as expected.
            
            title: str or None
                Review title.
            
            folder: str
                Path to a folder were the review files will be placed.
            
            clear: bool
                If set to True previous temp files within specified folder will
                be deleted.
        """
        
        self._title = title
        self._folder = folder
        self._clear = clear
        self._html_file = None
        self._css_file = None
        self._section_level = 0
        self._table_name = None
        self._ddmap_sizes = set()
        self._converters = {}
        self._eds = eds
        
        # check EDS
        if self._eds is not None and not isinstance(self._eds, EDS):
            raise TypeError("EDS must be of type pyeds.EDS!")
    
    
    def __enter__(self):
        """Opens review within 'with' statement."""
        
        self.Open()
        return self
    
    
    def __exit__(self, exc_ty, exc_val, tb):
        """Closes review within 'with' statement ended."""
        
        self.Close()
    
    
    def Open(self):
        """Creates and opens review files."""
        
        # check if opened
        if self._html_file is not None:
            return
        
        # ensure folder exists
        if not os.path.exists(self._folder):
            os.makedirs(self._folder)
        
        # clear folder
        elif self._clear:
            self._clear_folder()
        
        # get paths
        html_path = os.path.join(self._folder, "index.html")
        css_path = os.path.join(self._folder, "styles.css")
        
        # clear previous
        if os.path.exists(html_path):
            os.remove(html_path)
        
        if os.path.exists(css_path):
            os.remove(css_path)
        
        # open files
        self._html_file = open(html_path, "a", encoding='utf-8')
        self._css_file = open(css_path, "a", encoding='utf-8')
        
        # initialize review
        self._initialize()
    
    
    def Close(self):
        """Finalizes and closes all review files."""
        
        # check if opened
        if self._html_file is None:
            return
        
        # finalize review
        self._finalize()
        
        # close HTML file
        self._html_file.close()
        self._html_file = None
        
        # close CSS file
        self._css_file.close()
        self._css_file = None
    
    
    def Show(self):
        """Shows final review in default browser."""
        
        # ensure closed and finalized
        self.Close()
        
        # get path
        path = os.path.join(self._folder, "index.html")
        path = os.path.abspath(path)
        
        # show in browser
        webbrowser.open('file://'+path, autoraise=1)
    
    
    def InsertHeader(self, text):
        """
        Inserts given text as a header of current section level.
        
        Args:
            text: str
                Header text.
        """
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # close table if necessary
        self._close_table()
        
        # get level
        level = min(6, self._section_level + 1)
        
        # make HTML
        html = "<h%s class=\"level%s\">%s</h%s>\n" % (level, self._section_level, text, level)
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertItem(self, item, hide=(), hierarchy=False, header=False, sortable=False):
        """
        Inserts item data.
        
        Args:
            item: pyeds.EntityItem
                Item to be added.
            
            hide: (str,)
                Names of the properties to hide.
            
            hierarchy: bool
                If set to True all the item children will be inserted as well
                and corresponding sections will be created automatically.
            
            header: bool or str
                Specifies if a header should be shown before the newly created
                table. The value can be either custom string to be shown, True
                to automatically use the display name of the item or False to
                disable the header.
            
            sortable: bool
                If set to True, newly opened table allows user sorting by
                columns. Note that this is risky if subsequent table is added
                afterwards, which is related to the last item of parent table.
                This typically happens if the whole hierarchy is shown
                automatically.
        """
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get properties
        properties = self._get_item_properties(item, hide, False)
        
        # close table and init new if necessary
        if self._table_name != item.Type.Name:
            self._close_table()
            self._add_header(item, header)
            self._open_table(item.Type.Name, properties, sortable)
        
        # init row
        html = "      <tr>\n"
        
        # add properties
        for prop in properties:
            
            # get converter
            converter = self._get_prop_converter(prop)
            
            # get content
            content = self._get_prop_value(prop, converter)
            
            # get CSS
            cls = self._get_cell_class(prop, converter)
            style = converter.GetCellStyle(prop) if converter else None
            
            # make HTML
            html += "        <td class=\"%s\" style=\"%s\">%s</td>\n" % (cls, style, content)
            
            # add DDMap CSS
            if prop.Type.SpecialValueTypeName == "DataDistribution":
                self._add_ddmap_css(prop)
        
        # finalize row
        html += "      </tr>\n"
        
        # write to HTML file
        self._html_file.write(html)
        
        # show children
        if hierarchy and item.Children:
            self.OpenSection()
            self.InsertItems(item.Children, hide, True, header)
            self.CloseSection()
    
    
    def InsertItems(self, items, hide=(), hierarchy=False, header=False, sortable=False):
        """
        Inserts items data.
        
        Args:
            items: (pyeds.EntityItem,)
                Items to be added.
            
            hide: (str,)
                Names of the properties to hide.
            
            hierarchy: bool
                If set to True all the item children will be inserted as well
                and corresponding sections will be created.
            
            header: bool or str
                Specifies if a header should be shown before the newly created
                table. The value can be either custom string to be shown, True
                to automatically use the display name of the item or False to
                disable the header.
            
            sortable: bool
                If set to True, newly opened table allows user sorting by
                columns. Note that this is risky if subsequent table is added
                afterwards, which is related to the last item of parent table.
                This typically happens if the whole hierarchy is shown
                automatically.
        """
        
        for item in items:
            self.InsertItem(item, hide, hierarchy, header, sortable)
    
    
    def InsertImage(self, image_data, format='svg'):
        """
        Insert image.
        
        Args:
            image_data: str or binary
                Image data.
            
            format: str
                Image format (e.g. svg, png, jpg)
        """
        
        # check image
        if not image_data:
            return
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # close table if necessary
        self._close_table()
        
        # save image
        html = "  %s\n" % self._add_image(image_data, format)
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertItemImage(self, item, converter=None, **kwargs):
        """
        Inserts item as image using available converter.
        
        Args:
            item: pyeds.EntityItem
                Item to be added.
            
            converter: pyeds.ImageValueConverter or None
                Specific value converter or None to use the one registered for
                the entity type.
            
            kwargs: dict
                Keyword arguments to be forwarded into converter.
        """
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # close table if necessary
        self._close_table()
        
        # get converter by entity type
        if converter is None:
            converter = self._converters.get(item.Type.GUID, None)
        
        if converter is None:
            converter = self._converters.get(item.Type.Name, None)
        
        if converter is None:
            converter = self._converters.get(item.Type.DisplayName, None)
        
        # skip if no converter found
        if converter is None:
            return
        
        # check converter
        if not isinstance(converter, ImageValueConverter):
            raise TypeError("Converter mus be derived from 'pyeds.ImageValueConverter'!")
        
        # get image_data
        image_data = converter.Convert(item, **kwargs)
        
        # insert image
        self.InsertImage(image_data, converter.IMAGE_FORMAT)
    
    
    def InsertSpacer(self, height="2em"):
        """
        Inserts custom spacer.
        
        Args:
            height: str
                CSS height including units (e.g. 2em).
        """
        
        # assert open
        self._assert_opened()
        
        # close table if necessary
        self._close_table()
        
        # write to HTML file
        self._html_file.write("  <div class=\"spacer\" style=\"height: %s;\"></div>\n\n" % height)
    
    
    def InsertLine(self, height="1px", color="#aaa", style="solid"):
        """
        Inserts custom line.
        
        Args:
            height: str
                CSS height including units (e.g. 2em).
            
            color: str
                CSS color (e.g. #aaa).
            
            style: str
                CSS style (e.g. solid).
        """
        
        # assert open
        self._assert_opened()
        
        # close table if necessary
        self._close_table()
        
        # write to HTML file
        self._html_file.write("  <div class=\"line\" style=\"border-top: %s %s %s;\"></div>\n\n" % (height, style, color))
    
    
    def InsertPageBreak(self):
        """Inserts page break for printing."""
        
        # assert open
        self._assert_opened()
        
        # close table if necessary
        self._close_table()
        
        # write to HTML file
        self._html_file.write("  <div class=\"pagebreak\"></div>\n\n")
    
    
    def Section(self):
        """Opens sub-section within 'with' statement."""
        
        return SectionState(self)
    
    
    def OpenSection(self):
        """Opens sub-section."""
        
        # assert open
        self._assert_opened()
        
        # close current table
        self._close_table()
        
        # increase current level
        self._section_level += 1
    
    
    def CloseSection(self):
        """Closes sub-section."""
        
        # assert open
        self._assert_opened()
        
        # close current table
        self._close_table()
        
        # decrease current level
        if self._section_level:
            self._section_level -= 1
    
    
    def CloseTable(self):
        """Closes last table."""
        
        # assert open
        self._assert_opened()
        
        # close current table
        self._close_table()
    
    
    def _assert_opened(self):
        """Asserts HTML file is opened."""
        
        if self._html_file is None:
            raise ValueError("Review file is not opened!")
    
    
    def _clear_folder(self):
        """Removes all temp files having GUID as name."""
        
        # list folder
        for name in os.listdir(self._folder):
            
            # get basename and extension
            basename, extension = os.path.splitext(name)
            
            # remove matching names
            if GUID_PATTERN.match(basename):
                os.remove(os.path.join(self._folder, name))
    
    
    def _initialize(self):
        """Initializes review files."""
        
        # init HTML
        html = '<?xml version="1.0" encoding="utf-8"?>\n'
        html += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        html += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n'
        html += '<head>\n'
        html += '  <meta http-equiv="content-type" content="text/html; charset=utf-8" />\n'
        html += '  <title>%s</title>\n' % self._title
        html += '  <link rel="stylesheet" type="text/css" media="all" href="styles.css" />\n'
        html += '  <script type="text/javascript" src="scripts.js"></script>\n'
        html += '</head>\n'
        html += '\n'
        html += '<body>\n'
        html += '  <h1>%s</h1>\n\n' % self._title
        
        # write to HTML file
        self._html_file.write(html)
        
        # read main CSS
        path = os.path.join(os.path.dirname(__file__), "styles.css")
        with open(path) as f:
            css = f.read()
        
        # write to CSS file
        self._css_file.write(css)
        
        # copy scripts
        src_path = os.path.join(os.path.dirname(__file__), "scripts.js")
        dst_path = os.path.join(self._folder, "scripts.js")
        shutil.copy(src_path, dst_path)
        
        # initialize value converters
        self._converters = {}
        for guid in CONVERTERS:
            self._converters[guid] = CONVERTERS[guid](self._eds)
    
    
    def _finalize(self):
        """Finalizes review files."""
        
        # close opened table
        self._close_table()
        
        # finalize HTML
        html = '</body>\n'
        html += '</html>\n'
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def _open_table(self, name, properties, sortable=False):
        """Starts new table."""
        
        # remember table
        self._table_name = name
        
        # set sorting class
        sortable = " sortable" if sortable else ""
        
        # init table
        html = "  <table class=\"level%d%s\">\n" % (self._section_level, sortable)
        html += "    <thead>\n"
        html += "      <tr>\n"
        
        # add headers
        for prop in properties:
            title = prop.Type.Description or ""
            name = prop.Type.DisplayName if prop.Type.DisplayName else prop.Type.ColumnName
            html += "        <th title=\"%s\">%s</th>\n" % (title, name)
        
        # finalize table header
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def _close_table(self):
        """Closes current table."""
        
        # check if any
        if not self._table_name:
            return
        
        # finalize table
        html = "    </tbody>\n"
        html += "  </table>\n\n"
        
        # reset table name
        self._table_name = None
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def _add_header(self, item, header):
        """Inserts header based on item."""
        
        # check value
        if not header:
            return
        
        # get header from item
        if header is True:
            header = item.Type.DisplayName
        
        # add header
        if header:
            self.InsertHeader(header)
    
    
    def _add_image(self, image_data, extension='svg'):
        """Inserts given image and make HTML."""
        
        # make filename
        filename = "%s.%s" % (str(uuid.uuid4()), extension)
        path = os.path.join(self._folder, filename)
        
        # save image text
        if isinstance(image_data, str):
            with open(path, "w", encoding='utf-8') as f:
                f.write(image_data)
        
        # save binary image
        else:
            with open(path, 'wb') as f:
                f.write(image_data)
        
        # make html
        return "<img src=\"%s\" />" % filename
    
    
    def _add_ddmap_css(self, prop):
        """Adds CSS for new DDMap."""
        
        # get size
        size = len(prop.Type.SpecialValueType.Boxes)
        
        # check if new
        if size in self._ddmap_sizes:
            return
        
        # make css
        css = ".ddmap td:first-child:nth-last-child(%s),\n" % size
        css += ".ddmap td:first-child:nth-last-child(%s) ~ td{width: %.2f%%;}\n\n" % (size, 100./size)
        
        # write to CSS file
        self._css_file.write(css)
        
        # remember current size
        self._ddmap_sizes.add(size)
    
    
    def _get_item_properties(self, item, hide, autohide):
        """Gets available item properties."""
        
        # check hide
        if hide is None:
            hide = ()
        
        # get properties
        properties = []
        for prop in item.GetProperties():
            
            # autohide
            if autohide and prop.Type.DataVisibility in (0, 1):
                continue
            
            # check if hidden
            if prop.Type.ColumnName in hide or prop.Type.DisplayName in hide:
                continue
            
            properties.append(prop)
        
        # sort properties
        properties.sort(key=lambda x: x.Type.VisiblePosition)
        
        return properties
    
    
    def _get_prop_converter(self, prop):
        """Get property converter."""
        
        # get by editor GUID
        if prop.Type.GridCellControlGuid in self._converters:
            return self._converters[prop.Type.GridCellControlGuid]
        
        # get by data purpose
        elif prop.Type.DataPurpose in self._converters:
            return self._converters[prop.Type.DataPurpose]
        
        # get by special type name (enum, ddmap etc.)
        elif prop.Type.SpecialValueTypeName in self._converters:
            return self._converters[prop.Type.SpecialValueTypeName]
        
        # get by value type GUID
        elif prop.Type.ValueTypeGuid in self._converters:
            return self._converters[prop.Type.ValueTypeGuid]
        
        # use FormatString as template
        elif prop.Type.CustomDataType is None:
            return self._converters['Template']
        
        # get by basic type name (int, string etc.)
        elif prop.Type.CustomDataType.Name in self._converters:
            return self._converters[prop.Type.CustomDataType.Name]
        
        return None
    
    
    def _get_prop_value(self, prop, converter):
        """Formats property value."""
        
        # no converter available
        if converter is None:
            if prop.Value is None:
                return ""
            return escape(str(prop.Value))
        
        # convert value
        value = converter.Convert(prop)
        if value is None:
            return ""
        
        # add as image
        if isinstance(converter, ImageValueConverter):
            value = self._add_image(value, converter.IMAGE_FORMAT)
        
        # return final value
        return value
    
    
    def _get_cell_class(self, prop, converter):
        """Gets CSS classes for table cell."""
        
        # init classes
        classes = []
        
        # get from converter
        if converter is not None:
            cell_class = converter.GetCellClass(prop)
            if cell_class:
                classes += cell_class.split()
        
        # get from alignment
        alignments = {1: 'left', 2: 'center', 3: 'right', 4: 'stretch'}
        if prop.Type.TextHAlign in alignments:
            
            alignments_values = set(alignments.values())
            if all(c not in alignments_values for c in classes):
                classes.append(alignments[prop.Type.TextHAlign])
        
        return " ".join(classes)


class SectionState(object):
    """A helper class to allow using 'with' statement for review sections."""
    
    
    def __init__(self, review):
        """Initializes a new instance of SectionState."""
        
        self._review = review
    
    
    def __enter__(self):
        """Opens new section within 'with' statement."""
        
        self._review.OpenSection()
        return self
    
    
    def __exit__(self, exc_ty, exc_val, tb):
        """Closes last section within 'with' statement ended."""
        
        self._review.CloseSection()
