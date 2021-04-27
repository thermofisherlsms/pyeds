#  Created by Martin Strohalm, Thermo Fisher Scientific

# import module
import re
import pyeds


@pyeds.review.register("ResultItemDataPurpose/ElementalCompositionFormula")
class MyFormulaConverter(pyeds.review.StringValueConverter):
    """Formats elemental composition formula to use subscript."""
    
    def Convert(self, prop, **kwargs):
        """Converts given property value."""
        
        # check value
        if prop.Value is None:
            return ""
        
        # remove spaces
        formula = prop.Value.replace(" ", "&nbsp;")
        
        # use subscript
        formula = re.sub(r"(\d+)",  r"<sub>\1</sub>", formula)
        
        return formula


# init tools
eds = pyeds.EDS("data.cdResult")
review = pyeds.Review()

# open result file and review using the 'with' statement
with eds, review:
    
    items = eds.Read("ConsolidatedUnknownCompoundItem", limit=10)
    hide = ["Checked", "RTTolerance", "GroupAreas"]
    review.InsertItems(items, hide=hide)

# show review
review.Show()
