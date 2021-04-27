#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# init tools
eds = pyeds.EDS("data.cdResult")
review = pyeds.Review()

# open result file and review using the 'with' statement
with eds, review:
    
    # read traces
    path = ("SpecializedTraceItem", "XicTraceItem")
    items = eds.ReadHierarchy(path)
    
    # insert items
    for item in items:
        
        # insert item
        review.InsertItem(item)
        
        # insert trace image (requires matplotlib)
        review.InsertItemImage(item.Children[0])

# show review
review.Show()
