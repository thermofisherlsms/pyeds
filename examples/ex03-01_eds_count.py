#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.EDS("data.cdResult") as eds:
    
    # count all items
    print(eds.Count("ConsolidatedUnknownCompoundItem"))
    
    # count filtered
    query = "RetentionTime > 3.5 AND RetentionTime < 4.0"
    print(eds.Count("ConsolidatedUnknownCompoundItem", query=query))


# Please note that the 'query' provided for filtered reading is not a real SQL
# statement but rather its simplified version. It is now limited just to use
# the column names, values defined by '[A-Za-z0-9-_\.%]+', single quotes,
# grouping by '()' and following operators
#     'AND | OR'
#     'IS NULL | IS NOT NULL'
#     '<= | >= | != | = | < | > | LIKE'.
