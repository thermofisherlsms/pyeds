#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# init tools
eds = pyeds.EDS("data.cdResult")
review = pyeds.Review(eds)

# open result file and review using the 'with' statement
with eds, review:
    
    # Starting with CD 3.3.3 the real spectrum data are stored in a separate
    # unlinked table. To get them, you need to read linked spectrum info first
    # and separately read the spectrum data using the same IDs. For PD, this is
    # similar, except that real spectra are stored in separate "details" file.
    # to read them, you need to initialize a separate EDS for the details file.
    
    # read scan info
    path = ["ConsolidatedUnknownCompoundItem", "BestHitIonInstanceItem", "MassSpectrumInfoItem"]
    keep = ["MassSpectrumInfoItem"]
    queries = {"ConsolidatedUnknownCompoundItem": "ID = 1"}
    
    items = eds.ReadHierarchy(path, keep=keep, queries=queries)
    
    # read spectrum data
    ids = [d.IDs for d in items]
    spectra = eds.ReadMany("MassSpectrumItem", ids)
    
    # insert items
    for spectrum in spectra:
        
        # insert item
        review.InsertItem(spectrum, hide=['Spectrum'])
        
        # insert spectrum image (requires matplotlib)
        review.InsertItemImage(spectrum, title="")

# show review
review.Show()
