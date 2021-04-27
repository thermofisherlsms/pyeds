#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # read all items iterator
    items = eds.Read("ConsolidatedUnknownCompoundItem")
    print(items)
    print("")
    
    # advanced reading
    # - apply filter
    # - read selected properties only
    # - specify order
    # - specify limit and offset
    items = list(eds.Read("ConsolidatedUnknownCompoundItem",
        query = "RetentionTime > 3.8 AND RetentionTime < 4.1",
        properties = ["MolecularWeight", "RetentionTime", "MaxArea"],
        order = "MaxArea",
        desc = True,
        limit = 1,
        offset = 3))
    
    # access values directly
    for item in items:
        print(item.RetentionTime)
        print(item.GetValue('RetentionTime'))
        print(item['RetentionTime'])
        print("")
    
    # access full property
    for item in items:
        prop = item.GetProperty('RetentionTime')
        print(prop)
        print(type(prop))
        print(type(prop.Value))
        print(type(prop.Type))
        print(item.GetProperties("ResultItemDataPurpose/RetentionTime"))
        print("")
