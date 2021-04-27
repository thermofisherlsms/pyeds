#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# read report schema
report = pyeds.Report("data.cdResult")

# get specific data type
data_type = report.GetDataType("ConsolidatedUnknownCompoundItem")

# show all columns
for column in data_type.Columns:
    print(column.DisplayName)

# get column by name
print("")
print(data_type.GetColumn("ElementalCompositionFormula"))

# get columns by data purpose
print("")
for column in data_type.GetColumns("ResultItemDataPurpose/ElementalCompositionFormula"):
    print(column)
