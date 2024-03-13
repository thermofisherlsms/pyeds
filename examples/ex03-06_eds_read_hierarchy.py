#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # get path (be careful while using this method as it only follows the graph, not data logic)
    via = ["BestHitIonInstanceItem"]
    path = eds.GetPath("ConsolidatedUnknownCompoundItem", "MassSpectrumInfoItem", via)
    print(path)
    
    # read selected types only
    keep = ["ConsolidatedUnknownCompoundItem", "MassSpectrumInfoItem"]
    
    # read MS2 only
    queries = {"BestHitIonInstanceItem": "BestHitType = 2", "MassSpectrumInfoItem": "MSOrder = 2"}
    
    # read most abundant items
    orders = {"ConsolidatedUnknownCompoundItem": "MaxArea"}
    descs = {"ConsolidatedUnknownCompoundItem": True}
    
    # read top 2
    limits = {"ConsolidatedUnknownCompoundItem": 2}
    
    # read data
    items = eds.ReadHierarchy(path, keep=keep, queries=queries, orders=orders, descs=descs, limits=limits)
    for item in items:
        print(item.ElementalCompositionFormula)
        
        # access next type as child
        for child in item.Children:
            print("\t%s @%.3f min" % (child.MSOrder.DisplayName, child.RetentionTime))
