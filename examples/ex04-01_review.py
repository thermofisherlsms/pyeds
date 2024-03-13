#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# init tools
eds = pyeds.EDS("data.cdResult")
review = pyeds.Review(eds)

# open result file and review using the 'with' statement
with eds, review:
    
    # read and insert samples
    samples = list(eds.Read("WorkflowInputFile"))
    hide = ["RetentionTimeRange", "SoftwareRevision", "InstrumentHardware", "PhysicalFileName", "WorkflowID", "WorkflowLevel", "ChildWorkflowID"]
    
    review.InsertHeader("Sample Files")
    review.InsertItems(samples, hide=hide, sortable=True)
    
    # read and insert compounds
    compounds = list(eds.Read("ConsolidatedUnknownCompoundItem", limit=3, order="MaxArea", desc=True))
    hide = ["Checked", "RTTolerance", "GroupAreas"]
    
    review.InsertHeader("Selected Compounds")
    review.InsertItems(compounds, hide=hide)
    
    # read compound details
    parent = compounds[1]
    path = ["ConsolidatedUnknownCompoundItem", "UnknownCompoundInstanceItem", "UnknownCompoundIonInstanceItem", "ChromatogramPeakItem", "MassSpectrumInfoItem"]
    details = list(eds.ReadHierarchy(path, parent))
    
    # insert parent compound
    review.InsertHeader("Compound Details")
    review.InsertItem(parent)
    
    # insert compounds per file
    with review.Section():
        
        for item1 in details:
            review.InsertItem(item1)
            
            if not item1.Children:
                continue
            
            # insert features
            with review.Section():
                
                for item2 in item1.Children:
                    review.InsertItem(item2)
                    
                    if not item2.Children:
                        continue
                    
                    # insert peaks
                    with review.Section():
                        
                        for item3 in item2.Children:
                            review.InsertItem(item3, hide=["PeakModel"])
                            
                            if not item3.Children:
                                continue
                            
                            # insert scan info
                            with review.Section():
                                for item4 in item3.Children:
                                    review.InsertItem(item4)

# show review
review.Show()
