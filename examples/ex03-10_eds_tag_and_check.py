#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # read most abundant item
    item = next(eds.Read("ConsolidatedUnknownCompoundItem",
        order = "Area (Max.)",
        desc = True,
        limit = 1))
    
    # show original state
    print("Checked:", item.Checked)
    print("Tags:", item.Tags.Values if item.Tags else None)
    
    # check item
    item.Check(True)
    
    # turn on/off some tags
    item.Tag(0, True)
    item.Tag(4, False)
    
    # show new state
    print()
    print("Checked:", item.Checked)
    print("Tags:", item.Tags.Values)
    
    # backup data first!
    eds.Report.Backup()
    
    # update item in result database
    eds.Update([item])
