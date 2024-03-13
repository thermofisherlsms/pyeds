#  Created by Martin Strohalm, Thermo Fisher Scientific

import unittest
import pyeds


class TestCase(unittest.TestCase):
    """Test case for pyeds.EDS class."""
    
    
    def setUp(self):
        """Prepare test case data."""
        
        self.result_file = "../examples/data.cdResult"
    
    
    def test_count(self):
        """Tests whether Count works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            count = eds.Count("ConsolidatedUnknownCompoundItem")
            self.assertEqual(count, 1241)
            
            count = eds.Count("Compounds")
            self.assertEqual(count, 1241)
    
    
    def test_count_query(self):
        """Tests whether Count works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            query = "Name != ''"
            count = eds.Count("ConsolidatedUnknownCompoundItem", query)
            self.assertEqual(count, 248)
    
    
    def test_count_query_view(self):
        """Tests whether Count works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            query = "Checked = 1"
            count = eds.Count("ConsolidatedUnknownCompoundItem", query)
            self.assertEqual(count, 3)
    
    
    def test_count_connections(self):
        """Tests whether CountConnections works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            count = eds.CountConnections("ConsolidatedUnknownCompoundItem", "ChemSpiderResultItem")
            self.assertEqual(count, 1148)
            
            count = eds.CountConnections("Compounds", "ChemSpider Results")
            self.assertEqual(count, 1148)
    
    
    def test_count_connections_query(self):
        """Tests whether CountConnections works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            query = "DeltaMassInPPM < 1 AND DeltaMassInPPM > -1"
            count = eds.CountConnections("ConsolidatedUnknownCompoundItem", "ChemSpiderResultItem", query)
            self.assertEqual(count, 448)


# run test case
if __name__ == "__main__":
    unittest.main(verbosity=2)
