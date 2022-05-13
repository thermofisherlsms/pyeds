#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # Although it's not recommended, the display names can be used for
    # tables and properties instead of real database names. Note that uniqueness
    # of display names isn't guarantied.
    
    print(eds.Count("Compounds"))
    
    items = list(eds.Read("Compounds",
        query = "'RT [min]' > 3.8 AND 'RT [min]' < 4.5",
        properties = ["Calc. MW", "RT [min]", "Area (Max.)", "Formula"],
        order = "Area (Max.)",
        desc = True,
        limit = 1))
    
    # access values by column name or display name
    for item in items:
        
        print(item.RetentionTime)
        print(item.GetValue('RT [min]'))
        
        print(item.Formula)
        print(item.ElementalCompositionFormula)
