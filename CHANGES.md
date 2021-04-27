# v0.15.0

21-03-31
- Fixed hierarchical reading if mixed table names are used.

21-03-16

- Enum properties are now returned as EnumValue instead of EnumElement.
- Better support for flags enums.


# v0.14.0

20-10-09
- Review converters can now be registered using ValueTypeGuid.
- Added default review converter to display arrays of numbers.

20-09-24
- Added review converter to display web links.
- Added review converter to display gap fill status.
- Draw boxes even if there is no value for item in review.

20-07-23
- Fixed orphan extended data reading.


# v0.13.0

20-05-19
- Global peak model parser.
- Additional convenient properties for ScanHeader, ScanEvent and PrecursorInfo.

20-05-18
- Possibility to hide enums, distribution maps or hidden types in schema graph.

20-04-20
- Fixed trace reading.

20-04-02
- Support for Gaussian PeakModel.
- Support for Interpolated PeakModel.
- Possibility to display traces with peaks in review.

20-04-02
- Redesigned PeakModel parsing.
- Support for Pyco PeakModel.
- EntityItem.Properties now returns all properties as PropertyValue instead of just name.


# v0.12.0

20-03-10
- Using Review converters for custom values in EntityItem.

20-03-06
- Simple table sorting possible in Review and Summary.

20-03-04
- Reading extended data for PropertyColumn.
- Reading extended data for DataDistributionBox.
- Added review converter to display custom tags.
- Added review converter to display checked state.
- Added review converter to display delta mass.

20-01-29
- Fixed review of null data distribution map.
- Fixed review of null status map.
- Added grouping of status distribution maps.

19-11-11
- GetValue method of EntityItem returns default if not found.

19-11-06
- Specific columns can be excluded from EDS reading.
- Added 'InsertSpacer' method to add spacer into review.
- Added 'InsertLine' method to add horizontal line into review.

19-11-05
- Possibility to add custom values to EntityItem to be displayed in Review.
- Retrieving all properties by EntityItem.GetProperties() if data purpose is None.
- Fix to include connection properties for EntityItem.GetProperties() method.
- CustomDataType.Value renamed to CustomDataType.ID.

# v0.11.0

19-10-23
- Avoiding Matplotlib warnings.

19-10-15
- Small improvements in summary.

19-08-12
- Using 'with' statement to create sections in Review.


# v0.10.0

19-04-11
- Support for using display names for tables and properties.
- Quoting all SQL statements.


# v0.9.0

19-03-18
- Fixed reading of empty MOL structures.
- Showing all available properties on simple printing of EntityItem.


# v0.8.0

19-02-07
- Additional information retrieved from spectrum XML.
- MassSpectrum object now mimics original XML using Header, Event, Precursor.
- For each unknown attribute of MassSpectrum, the Header and Event are searched.
- Support for 0.## formatting string.
- Avoid crash if no levels defined for data distribution map.

19-02-06
- Avoid crash if WF message should be set to non-existing WF.


# v0.7.0

19-01-16
- Switched to Python 3.


# v0.6.0

18-12-19
- Added review converter to display MassSpectrumItem as Matplotlib image.
- Added review converter to display XicTraceItem as Matplotlib image.


# v0.5.0

18-12-18
- Workflows definitions are now available via Report.Workflows.
- Workflows definitions can be shown in Summary.
- Added method Summary.ShowSchema() to show data types and schema only.
- Added method Summary.ShowWorkflows() to show workflows only.
- DataType.DataTypeIdentifier renamed to DataType.GUID.


# v0.4.0

18-11-26
- Values of entity properties are now accessed directly (no need for .Value).
- The EntityItem.GetValue(str) method gives now actual value.
- Added EntityItem.GetProperty(str) method to get full property.
- Values for data distribution maps are now given as DataDistributionValue.
- EntityItem and PropertyValue instances are now read-only.

18-11-05
- Added EntityItem.GetProperties(str) method to get values by data purpose.


18-11-02
- Added DataType.GetColumns(str) method to get columns by data purpose.

18-10-25
- Added property 'IDs' to get unique ID values of EntityItem.
- Added equality comparer for EnumElement (for int or another EnumElement).


# v0.3.0

18-10-19
- Fixed parsing of RetentionTimeRasterItem.

18-10-16
- Removed pysqlite requirement.

18-10-15
- DataPurpose can now be used to register report converters.


# v0.2.0

18-10-12
- Added converter to read peak models.

18-10-11
- Added converter to read arrays of doubles.
- Added converter to read arrays of integers.


# v0.1.0

18-09-13
- Initial version of setup.py to create a distributable package.

18-09-12
- DDMapConverter now displays cells even if the whole value is not set.
- DDMapConverter now displays gray cell if no box value is set.
- Changed the way table class is given for DDMapConverter.

18-09-07
- Adding additional precursor information into scan header.

18-08-20
- DataPurpose can now be used to register review converters.
- Added review converter for ElementalCompositionFormula.
- Renamed 'ReportFile' to 'Report'.

18-08-13
- Fixed spectrum profile reading.

18-08-07
- Added MOL string validation into structure converter.

18-07-24
- Added native converter to read mass spectra.
- Added native converter to read isotope patterns.
- Added native converter to read traces.
- Revised examples.

18-07-23
- Graph updated to D3js v5.5.

18-07-20
- Improved documentation.
- BoxID and LevelID renamed to ID.

18-07-17
- Converters are now registered under original, lower-cased and upper-cased key.

18-07-16
- Using BytesIO to decompress zipped data.
- PeakModel value is now returned as unzipped XML.

18-03-14
- ReadHierarchy now returns all items if "keep" is set to None.

18-01-10
- Renamed 'PropertyColumn.ColumnID' to 'PropertyColumn.ID'.
- Renamed 'EnumDataType.EnumID' to 'EnumDataType.ID'.
- Renamed 'EnumDataType.EnumTypeName' to 'EnumDataType.TypeName'.

17-12-05
- Review can now automatically insert headers before tables.
- Header margins adjusted in review.
- Revised ValueConverter design for ReportFile and Review.

17-12-04
- Enum properties now returns corresponding EnumElement.
- Data distribution map properties now returns tuple of values.
- ReadHierarchy now does not return parent if not specified in "keep".
- Renamed 'CreateItem' methods to 'Convert'.

17-11-30
- Report file schema objects are now read-only.

17-11-24
- Using relative paths for module imports.
- Review by default doesn't show the full item hierarchy.
- Minimum header font size is now limited in review.

17-10-25
- Support for 'IS NULL' and 'IS NOT NULL' in query.
- Support for '' (empty string) in query.

17-08-29
- Added 'InsertImage' method to add images into review.
- Added 'InsertItemImage' method to create and add images into review.
- Added 'InsertPageBreak' method to force page-break in review printing.
- Renamed 'OpenSubSection' to 'OpenSection' in review and summary.
- Renamed 'CloseSubSection' to 'CloseSection' in review and summary.
- Avoid page-breaks right after table header.

17-08-28
- Added 'RawValue' property to access original value as stored in report file.

17-08-11
- Allow "[]+-"" within query quote.
- Review can now show full item hierarchy automatically.
- ReadHierarchy now allows to read all items of type if no parent is given.
- ReadHierarchy now allows to specify order, desc, limit and offset.
- ReadHierarchy now returns generator, same as other readers.

17-05-12
- Added local copy of d3.v3.min.js for connection graph to work off-line.

17-05-05
- Fixed conversion of zipped data if value is None.

17-03-22
- Added 'Converter GUID' into summary.
- Added support for registering and applying property value converters.
- Added converter to unzip IsotopePattern into XML string.
- Added converter to unzip MassSpectrum into XML string.
- Added converter to unzip MolString into string.
- Added converter to parse Trace into list of TracePoint.
- Fixed 'hide' parameter for 'InsertItems' method of review.

17-02-27
- Mol structure converter can now handle both "uncharged" and "charged" editors.

17-02-03
- Data type pops up in connection graph if hovered in the main table.

17-01-03
- Fixed reading of distribution map if the value is NULL.

16-11-09
- Added 'Formating' string into summary.

16-10-26
- Fixed mol structure unzipping.

16-10-11
- Improved documentation.
- All properties are retrieved by default for the last item in hierarchy reader.
- Review folder path is added to property converters by Initialize method.

16-10-09
- Better check for query syntax.
- Added equality comparer for PropertyValue.
- Safer way of deleting previous temp files from review.

16-09-30
- Mol structure converter now checks for type.

16-09-20
- Showing molecular structure as image in review.

16-09-19
- Showing connection columns in summary.
- Connection graph has now active links to connection details.
- Added review folder path to property converters.

16-09-16
- Improved tooltip for data distribution maps in review.
- Added baseclass for status-type enums converters.

16-09-08
- Enums are now sorted alphabetically in summary.

16-08-25
- Main converters for enums and data distribution maps are now registered and
  used as a fallback for corresponding properties instead of just strings.
- SMILES string is used to represent structures. Requires RDKit.

16-07-12
- Connection graph reflects items count as node size.
- Using Alt to fix position of a node in connection graph.
- Items count shown in tooltip in connection graph.
- Added tooltip for links in connection graph.

16-07-10
- Connection graph added into summary.

16-07-05
- Each read/execute request now returns new cursor.

16-06-23
- Added simple HTML summary tool.
- Fixed color conversion.

16-06-20
- Generic implementation of DDMap value converter.
- Last level is used in DDMap as fallback.
- Added few more value converters for review.
- Avoid printing of None in review.
- Right alignment of DDMap values.

16-06-18
- All EntityItem properties are now stored as PropertyValue instead of direct type.
- Added simple HTML reporting tool.
- Added Guid to PropertyColumn.
- Added GetLevel method for DataDistributionMap.
- DataDistributionMapItem.Value renamed to DataDistributionMapItem.Values.
- EntityItem.Connections renamed to EntityItem.Children.
- EnumDataType.Values renamed to EnumDataType.Elements.
- EnumDataType.AddValue renamed to EnumDataType.AddElement.
- EnumDataType.GetValue renamed to EnumDataType.GetElement.

16-06-14
- Fixed SQL with ORDER BY.
- Added unzipping of simple stream.

16-05-25
- Initial version.
