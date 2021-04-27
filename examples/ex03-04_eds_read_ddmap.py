#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # read single item
    item = next(eds.Read("ConsolidatedUnknownCompoundItem", limit=1))
    
    # access ddmap value
    print(type(item.Area))
    print(item.Area.Values)
    print(item.Area[0])
    print(item.Area.GetValue(0))
    print(item.Area.GetBox(0).Name)
    print(item.Area.GetLevel(0).Name)
    print("")
    
    # access ddmap of 'enums-like'
    print(type(item.AnnotationMatchStatus))
    print(item.AnnotationMatchStatus.Values)
    print(type(item.AnnotationMatchStatus.GetValue(1)))
    print(item.AnnotationMatchStatus.GetBox(1).Name)
    print(item.AnnotationMatchStatus.GetLevel(1).Name)
