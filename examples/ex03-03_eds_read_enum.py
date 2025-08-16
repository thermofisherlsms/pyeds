#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # read single item
    item = next(eds.Read("MassSpectrumItem", limit=1))
    
    # show type
    print(type(item.MSOrder))
    print("")
    
    # access enum value
    print(item.MSOrder)
    print(item.MSOrder.Value)
    print(item.MSOrder.DisplayName)
    print("")
    
    # build-in comparison
    print(item.MSOrder == 1)
    print(item.MSOrder == "MS1")
    print(item.MSOrder.Contains(1))
    print(item.MSOrder.Contains("MS1"))
