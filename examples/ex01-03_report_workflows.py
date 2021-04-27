#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import pyeds

# read report schema
report = pyeds.Report("data.cdResult")

# get first workflow
workflow = report.Workflows[0]

# show nodes
for node in workflow.Nodes:
    print(node)

# get specific node
node = workflow.GetNode(4)

# show node params
print("")
print(node)
for param in node.Parameters:
    print("\t", param.DisplayName, ':', param.DisplayValue)
