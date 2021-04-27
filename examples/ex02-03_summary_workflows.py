#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# open result file using the 'with' statement
with pyeds.Summary("data.cdResult") as summary:
    
    # show workflow info
    summary.ShowWorkflows()
