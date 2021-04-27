#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds


@pyeds.report.register("ResultItemDataPurpose/RetentionTime")
@pyeds.report.register("ResultItemDataPurpose/LeftRetentionTime")
@pyeds.report.register("ResultItemDataPurpose/RightRetentionTime")
class MyRTConverter(pyeds.report.ValueConverter):
    """Converts retention time from minutes to seconds."""
    
    def Convert(self, value):
        """Converts given property value."""
        
        # check value
        if value is None:
            return None
        
        # convert value
        return value * 60


# read items
with pyeds.EDS("data.cdResult") as eds:
    
    items = eds.Read("ConsolidatedUnknownCompoundItem", limit=5)
    for item in items:
        prop = item.GetProperty('RetentionTime')
        print(item.RetentionTime, prop.Value, prop.RawValue)
