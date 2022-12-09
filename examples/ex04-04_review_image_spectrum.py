#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# init tools
eds = pyeds.EDS("data.cdResult")
review = pyeds.Review(eds)

# open result file and review using the 'with' statement
with eds, review:
    
    # read scans
    path = ["ConsolidatedUnknownCompoundItem", "BestHitIonInstanceItem", "MassSpectrumItem"]
    keep = ["MassSpectrumItem"]
    queries = {
        "ConsolidatedUnknownCompoundItem": "ID = 1",
        "BestHitIonInstanceItem": "BestHitType = 2"}
    
    items = eds.ReadHierarchy(path, keep=keep, queries=queries)
    
    # insert items
    for item in items:
        
        # insert item
        review.InsertItem(item, hide=['Spectrum'])
        
        # insert spectrum image (requires matplotlib)
        review.InsertItemImage(item, title="")

# show review
review.Show()
