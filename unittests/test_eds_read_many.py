#  Created by Martin Strohalm, Thermo Fisher Scientific

import unittest
import pyeds


class TestCase(unittest.TestCase):
    """Test case for pyeds.EDS class."""
    
    
    def setUp(self):
        """Prepare test case data."""
        
        self.result_file = "../examples/data.cdResult"
    
    
    def test_read_many(self):
        """Tests whether ReadMany works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            props = eds.Report.GetDataType("ChromatogramPeakItem").Columns
            ids = [item.IDs for item in eds.Read("ChromatogramPeakItem", limit=10)]
            
            items = eds.ReadMany("ChromatogramPeakItem", ids)
            for i, item in enumerate(items):
                self.assertEqual(ids[i], item.IDs)
                for prop in props:
                    self.assertTrue(item.HasProperty(prop.ColumnName))
            
            items = eds.ReadMany("Chromatogram Peaks", ids)
            for i, item in enumerate(items):
                self.assertEqual(ids[i], item.IDs)
                for prop in props:
                    self.assertTrue(item.HasProperty(prop.ColumnName))
    
    
    def test_read_many_properties(self):
        """Tests whether ReadMany works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            ids = [item.IDs for item in eds.Read("ChromatogramPeakItem", limit=10)]
            
            items = eds.ReadMany("ChromatogramPeakItem", ids, properties=["ApexRT", "FWHM"])
            for i, item in enumerate(items):
                self.assertEqual(ids[i], item.IDs)
                self.assertTrue(item.HasProperty("ID"))
                self.assertTrue(item.HasProperty("ApexRT"))
                self.assertTrue(item.HasProperty("FWHM"))
                self.assertFalse(item.HasProperty("LeftRT"))
            
            items = eds.ReadMany("Chromatogram Peaks", ids, properties=["Apex RT [min]", "FWHM [min]"])
            for i, item in enumerate(items):
                self.assertEqual(ids[i], item.IDs)
                self.assertTrue(item.HasProperty("ID"))
                self.assertTrue(item.HasProperty("ApexRT"))
                self.assertTrue(item.HasProperty("FWHM"))
                self.assertFalse(item.HasProperty("LeftRT"))
    
    
    def test_read_many_exclude(self):
        """Tests whether ReadMany works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            ids = [item.IDs for item in eds.Read("ChromatogramPeakItem", limit=10)]
            
            items = eds.ReadMany("ChromatogramPeakItem", ids, exclude=["ID", "ApexRT", "FWHM"])
            for i, item in enumerate(items):
                self.assertEqual(ids[i], item.IDs)
                self.assertTrue(item.HasProperty("ID"))
                self.assertFalse(item.HasProperty("ApexRT"))
                self.assertFalse(item.HasProperty("FWHM"))
                self.assertTrue(item.HasProperty("LeftRT"))
            
            items = eds.ReadMany("Chromatogram Peaks", ids, exclude=["ID", "Apex RT [min]", "FWHM [min]"])
            for i, item in enumerate(items):
                self.assertEqual(ids[i], item.IDs)
                self.assertTrue(item.HasProperty("ID"))
                self.assertFalse(item.HasProperty("ApexRT"))
                self.assertFalse(item.HasProperty("FWHM"))
                self.assertTrue(item.HasProperty("LeftRT"))


# run test case
if __name__ == "__main__":
    unittest.main(verbosity=2)
