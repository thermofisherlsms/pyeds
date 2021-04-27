#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# init tools
eds = pyeds.EDS("data.cdResult")
review = pyeds.Review()

# open result file and review using the 'with' statement
with eds, review:
    
    # read features
    features = eds.Read("UnknownCompoundIonInstanceItem", limit=1)
    for feature in features:
        
        # read traces
        traces = list(eds.ReadConnected("XicTraceItem", feature))
        
        # read peaks
        peaks = list(eds.ReadConnected("ChromatogramPeakItem", feature))
        
        # insert data
        review.InsertItem(feature)
        with review.Section():
            
            # insert peaks
            review.InsertItems(peaks)
            
            # insert trace image and draw combined peak (requires matplotlib)
            review.InsertItemImage(traces[0], peaks=[peaks])
            
            # insert trace image and draw individual peaks (requires matplotlib)
            # note that the haded area for Pyco peaks is incorrect since there is no model available
            left_rt = min(p.LeftRT for p in peaks)
            right_rt = max(p.RightRT for p in peaks)
            review.InsertItemImage(traces[0], peaks=peaks, zoom=(left_rt-0.25, right_rt+0.25))

# show review
review.Show()
