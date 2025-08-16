#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # read single item
    item = next(eds.Read("ConsolidatedUnknownCompoundItem", limit=1))
    
    # show type
    print(type(item.Area))
    print("")
    
    # access ddmap value
    print(item.Area)
    print(item.Area.Values)
    print(item.Area[0])
    print(item.Area.GetValue(0))
    print("")
    
    # access extra info
    print(item.Area.GetBox(0).Name)
    print(item.Area.GetLevel(0).Name)
    print("")
    
    # build-in iterator
    for value in item.Area:
        print(value)
    
    # access ddmap of 'enums-like'
    print(type(item.AnnotationMatchStatus))
    print(item.AnnotationMatchStatus.Values)
    print(type(item.AnnotationMatchStatus.GetValue(1)))
    print(item.AnnotationMatchStatus.GetBox(1).Name)
    print(item.AnnotationMatchStatus.GetLevel(1).Name)
