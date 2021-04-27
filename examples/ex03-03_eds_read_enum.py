#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # read single item
    item = next(eds.Read("MassSpectrumItem", limit=1))
    
    # access enum value
    print(type(item.MSOrder))
    print(item.MSOrder.Value)
    print(item.MSOrder.DisplayName)
