#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# init tools
eds = pyeds.EDS("data.cdResult")
review = pyeds.Review(eds)

# open result file and review using the 'with' statement
with eds, review:
    
    # read items
    items = eds.Read("ConsolidatedUnknownCompoundItem", properties=["Name", "MolecularWeight", "RetentionTime", "Area", "Formula"], limit=5)
    for item in items:
        
        # add custom values
        item.AddValue(item.MolecularWeight+1.007276, "MZ [M+H]", align=3, template="{:.5f}")
        
        # insert item
        review.InsertItem(item, hide=['ID'])

# show review
review.Show()
