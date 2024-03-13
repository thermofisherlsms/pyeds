#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# init tools
eds = pyeds.EDS("data.cdResult")
review = pyeds.Review(eds)

# open result file and review using the 'with' statement
with eds, review:
    
    # read and automatically insert full hierarchy
    path = ["ConsolidatedUnknownCompoundItem", "UnknownCompoundInstanceItem", "UnknownCompoundIonInstanceItem", "ChromatogramPeakItem", "MassSpectrumInfoItem"]
    items = eds.ReadHierarchy(path, limits={"ConsolidatedUnknownCompoundItem": 1})
    
    hide = ["PeakModel"]
    review.InsertItems(items, hide=hide, hierarchy=True, header=True)

# show review
review.Show()
