#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # advanced query may contain information for sorting, limit and offset
    # in such case, values provided by corresponding parameters are ignored
    
    items = list(eds.Read("ConsolidatedUnknownCompoundItem",
        query = """
            RetentionTime > 3.8 AND RetentionTime < 4.1
            ORDER BY MaxArea DESC
            LIMIT 2
            OFFSET 3
            """))
    
    # print items
    for item in items:
        print(f"{item.ElementalCompositionFormula} @ {item.RetentionTime:.3f}, {item.MaxArea:.2e}")
