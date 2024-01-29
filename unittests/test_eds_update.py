#  Created by Martin Strohalm, Thermo Fisher Scientific

import unittest
import pyeds


class TestCase(unittest.TestCase):
    """Test case for pyeds.EDS class."""
    
    
    def setUp(self):
        """Prepare test case data."""
        
        self.result_file = "../examples/data.cdResult"
    
    
    def test_update(self):
        """Tests whether Update works correctly."""
        
        self._updateAndTest(["Name"])
    
    
    def test_update_view(self):
        """Tests whether Update works correctly."""
        
        self._updateAndTest(["Checked", "Tags"])
    
    
    def test_update_combi(self):
        """Tests whether Update works correctly."""
        
        self._updateAndTest(["Name", "Checked", "Tags"])
    
    
    def test_update_exclude(self):
        """Tests whether Update works correctly."""
        
        self._updateAndTest(["Name", "Checked", "Tags"], exclude=["Tags"])
    
    
    def _updateAndTest(self, props, exclude=()):
        """Loads, updates and tests items."""
        
        # get items
        with pyeds.EDS(self.result_file) as eds:
            items = list(eds.Read("ConsolidatedUnknownCompoundItem", limit=5))
        
        # update items
        self._updateItems(items, props, exclude)
        self._checkItems(items, props, exclude)
        
        # revert changes
        self._updateItems(items, props, exclude)
        self._checkItems(items, props, ())
    
    
    def _updateItems(self, items, props, exclude):
        """Updates selected properties of given items."""
        
        # update items
        for item in items:
            for name in props:
                
                if name == "Checked":
                    item.Check(not item.Checked)
                
                elif name == "Tags":
                    item.Tag(0, not item.Tagged(0))
                
                elif name == "Name" and item.Name.endswith("_EDS_MODIFIED"):
                    item.SetValue("Name", item.Name.replace("_EDS_MODIFIED", ""))
                
                elif name == "Name":
                    item.SetValue("Name", item.Name + "_EDS_MODIFIED")
        
        # check if flagged as dirty
        self._assertDirty(items, props, True)
        
        # get properties to save
        include = [p for p in props if p not in exclude]
        
        # update database
        with pyeds.EDS(self.result_file) as eds:
            eds.Update(items, include if exclude else None)
        
        # check if dirty flag reset
        self._assertDirty(items, include, False)
        self._assertDirty(items, exclude, True)
    
    
    def _checkItems(self, items, props, exclude):
        """Checks if items were updated properly."""
        
        # get updated properties
        include = [p for p in props if p not in exclude]
        
        # read and test items
        with pyeds.EDS(self.result_file) as eds:
            
            # read new items
            ids = [item.IDs for item in items]
            new_items = eds.ReadMany("ConsolidatedUnknownCompoundItem", ids)
            
            # test items
            for i, item in enumerate(new_items):
                
                # sanity check for IDs
                self.assertTrue((item.IDs == items[i].IDs))
                
                # check properties
                for name in include:
                    self.assertTrue(item.GetValue(name) == items[i].GetValue(name))
                for name in exclude:
                    self.assertFalse(item.GetValue(name) == items[i].GetValue(name))
    
    
    def _assertDirty(self, items, props, value):
        """Asserts given properties dirty or not."""
        
        for item in items:
            for name in props:
                prop = item.GetProperty(name)
                self.assertTrue(prop.IsDirty == value)


# run test case
if __name__ == "__main__":
    unittest.main(verbosity=2)
