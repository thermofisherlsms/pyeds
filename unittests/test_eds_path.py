#  Created by Martin Strohalm, Thermo Fisher Scientific

import unittest
import pyeds


class TestCase(unittest.TestCase):
    """Test case for pyeds.EDS class."""
    
    
    def setUp(self):
        """Prepare test case data."""
        
        self.result_file = "../examples/data.cdResult"
    
    
    def test_get_path(self):
        """Tests whether GetPath works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            model = ("ConsolidatedUnknownCompoundItem", "MissingCompoundIonInstanceItem", "XicTraceItem")
            
            path = eds.GetPath("ConsolidatedUnknownCompoundItem", "XicTraceItem")
            self.assertEqual(path, model)
            
            path = eds.GetPath("Compounds", "XIC Traces")
            self.assertEqual(path, model)
    
    
    def test_get_path_via(self):
        """Tests whether GetPath works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            model = ("ConsolidatedUnknownCompoundItem", "UnknownCompoundInstanceItem", "UnknownCompoundIonInstanceItem", "XicTraceItem")
            
            path = eds.GetPath("ConsolidatedUnknownCompoundItem", "XicTraceItem", via=["UnknownCompoundInstanceItem"])
            self.assertEqual(path, model)
            
            path = eds.GetPath("Compounds", "XIC Traces", via=["Compounds per File"])
            self.assertEqual(path, model)


# run test case
if __name__ == "__main__":
    unittest.main(verbosity=2)
