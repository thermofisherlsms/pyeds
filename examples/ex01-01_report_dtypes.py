#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# read report schema
report = pyeds.Report("data.cdResult")

# get all data types
for data_type in report.DataTypes:
    print(data_type)
