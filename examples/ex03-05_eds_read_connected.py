#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # get parent
    parent = next(eds.Read("ConsolidatedUnknownCompoundItem", query="ID = 1"))
    
    # read directly connected
    items = eds.ReadConnected("MzCloudSearchResultItem",
        parent = parent,
        query = "MzLibraryMatchFactor > 90",
        order = "MzLibraryMatchFactor",
        desc = True)
    
    for item in items:
        print(parent.Name, item.MatchTypeProperty.DisplayName, item.MzLibraryMatchFactor)
