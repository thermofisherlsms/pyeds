#  Created by Martin Strohalm, Thermo Fisher Scientific

import unittest
import pyeds


class TestCase(unittest.TestCase):
    """Test case for pyeds.EDS class."""
    
    
    def setUp(self):
        """Prepare test case data."""
        
        self.result_file = "../examples/data.cdResult"
    
    
    def test_read(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            props = eds.Report.GetDataType("ConsolidatedUnknownCompoundItem").Columns
            
            items = eds.Read("ConsolidatedUnknownCompoundItem")
            for i, item in enumerate(items):
                if i == 5: break
                for prop in props:
                    self.assertTrue(item.HasProperty(prop.ColumnName))
            
            items = eds.Read("Compounds")
            for i, item in enumerate(items):
                if i == 5: break
                for prop in props:
                    self.assertTrue(item.HasProperty(prop.ColumnName))
    
    
    def test_read_properties(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", properties=["Name", "ElementalCompositionFormula"])
            for i, item in enumerate(items):
                if i == 5: break
                self.assertTrue(item.HasProperty("ID"))
                self.assertTrue(item.HasProperty("Name"))
                self.assertTrue(item.HasProperty("ElementalCompositionFormula"))
                self.assertFalse(item.HasProperty("Structure"))
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", properties=["Name", "Formula"])
            for i, item in enumerate(items):
                if i == 5: break
                self.assertTrue(item.HasProperty("ID"))
                self.assertTrue(item.HasProperty("Name"))
                self.assertTrue(item.HasProperty("ElementalCompositionFormula"))
                self.assertFalse(item.HasProperty("Structure"))
    
    
    def test_read_exclude(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", exclude=["ID", "Name", "ElementalCompositionFormula"])
            for i, item in enumerate(items):
                if i == 5: break
                self.assertTrue(item.HasProperty("ID"))
                self.assertFalse(item.HasProperty("Name"))
                self.assertFalse(item.HasProperty("ElementalCompositionFormula"))
                self.assertTrue(item.HasProperty("Structure"))
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", exclude=["ID", "Name", "Formula"])
            for i, item in enumerate(items):
                if i == 5: break
                self.assertTrue(item.HasProperty("ID"))
                self.assertFalse(item.HasProperty("Name"))
                self.assertFalse(item.HasProperty("ElementalCompositionFormula"))
                self.assertTrue(item.HasProperty("Structure"))
    
    
    def test_read_order(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", order="MaxArea")
            last = 0
            for i, item in enumerate(items):
                if i == 100: break
                value = item.GetValue("MaxArea")
                self.assertGreaterEqual(value, last)
                last = value
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", order="Area (Max.)")
            last = 0
            for i, item in enumerate(items):
                if i == 100: break
                value = item.GetValue("Area (Max.)")
                self.assertGreaterEqual(value, last)
                last = value
    
    
    def test_read_order_desc(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", order="MaxArea", desc=True)
            last = float("inf")
            for i, item in enumerate(items):
                if i == 100: break
                value = item.GetValue("MaxArea")
                self.assertLessEqual(value, last)
                last = value
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", order="Area (Max.)", desc=True)
            last = float("inf")
            for i, item in enumerate(items):
                if i == 100: break
                value = item.GetValue("Area (Max.)")
                self.assertLessEqual(value, last)
                last = value
    
    
    def test_read_limit(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items15 = list(eds.Read("ConsolidatedUnknownCompoundItem", limit=5))
            self.assertEqual(len(items15), 5)
    
    
    def test_read_limit_offset(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items15 = list(eds.Read("ConsolidatedUnknownCompoundItem", limit=5))
            
            items35 = list(eds.Read("ConsolidatedUnknownCompoundItem", limit=3, offset=2))
            self.assertEqual(len(items35), 3)
            self.assertEqual(items35[0].ID, items15[2].ID)
            self.assertEqual(items35[1].ID, items15[3].ID)
            self.assertEqual(items35[2].ID, items15[4].ID)
    
    
    def test_read_query(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts = 2")
            for i, item in enumerate(items):
                self.assertEqual(item.GetValue("NumberOfAdducts"), 2)
            self.assertGreaterEqual(i, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="'# Adducts' = 2")
            for j, item in enumerate(items):
                self.assertEqual(item.GetValue("NumberOfAdducts"), 2)
            self.assertGreaterEqual(j, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="'Area (Max.)' > 1e6")
            for k, item in enumerate(items):
                self.assertGreater(item.GetValue("MaxArea"), 1e6)
            self.assertGreaterEqual(k, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="'RT [min]' > 3")
            for m, item in enumerate(items):
                self.assertGreater(item.GetValue("RetentionTime"), 3)
            self.assertGreaterEqual(m, 0)
    
    
    def test_read_query_view(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Checked = 1")
            for i, item in enumerate(items):
                self.assertEqual(item.GetValue("Checked"), 1)
            self.assertGreaterEqual(i, 0)
    
    
    def test_read_query_equals(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts = 2")
            for i, item in enumerate(items):
                self.assertEqual(item.GetValue("NumberOfAdducts"), 2)
            self.assertGreaterEqual(i, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts != 2")
            for j, item in enumerate(items):
                self.assertNotEqual(item.GetValue("NumberOfAdducts"), 2)
            self.assertGreaterEqual(j, 0)
    
    
    def test_read_query_range(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts < 2")
            for i, item in enumerate(items):
                self.assertLess(item.GetValue("NumberOfAdducts"), 2)
            self.assertGreaterEqual(i, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts <= 2")
            for j, item in enumerate(items):
                self.assertLessEqual(item.GetValue("NumberOfAdducts"), 2)
            self.assertGreaterEqual(j, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts > 2")
            for k, item in enumerate(items):
                self.assertGreater(item.GetValue("NumberOfAdducts"), 2)
            self.assertGreaterEqual(k, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts >= 2")
            for m, item in enumerate(items):
                self.assertGreaterEqual(item.GetValue("NumberOfAdducts"), 2)
            self.assertGreaterEqual(m, 0)
    
    
    def test_read_query_like(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Name LIKE '%ZOLE'")
            for i, item in enumerate(items):
                self.assertTrue(item.GetValue("Name").endswith('zole'))
            self.assertGreaterEqual(i, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Name LIKE 'peg%'")
            for j, item in enumerate(items):
                self.assertTrue(item.GetValue("Name").startswith('PEG'))
            self.assertGreaterEqual(j, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Name LIKE '%FFE%'")
            for k, item in enumerate(items):
                self.assertTrue('ffe' in item.GetValue("Name"))
            self.assertGreaterEqual(k, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Name NOT LIKE '%ZOLE'")
            for m, item in enumerate(items):
                self.assertFalse(item.GetValue("Name").endswith('zole'))
            self.assertGreaterEqual(m, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Name NOT LIKE 'OME%'")
            for n, item in enumerate(items):
                self.assertFalse(item.GetValue("Name").startswith('Ome'))
            self.assertGreaterEqual(n, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Name NOT LIKE '%FFE%'")
            for p, item in enumerate(items):
                self.assertFalse('ffe' in item.GetValue("Name"))
            self.assertGreaterEqual(p, 0)
    
    
    def test_read_query_in(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts IN (1, 2)")
            for i, item in enumerate(items):
                self.assertTrue(item.GetValue("NumberOfAdducts") in (1, 2))
            self.assertGreaterEqual(i, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts NOT IN (1, 2)")
            for j, item in enumerate(items):
                self.assertTrue(item.GetValue("NumberOfAdducts") not in (1, 2))
            self.assertGreaterEqual(j, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Name IN ('PEG n7', 'PEG n6')")
            for k, item in enumerate(items):
                self.assertTrue(item.GetValue("Name") in ('PEG n7', 'PEG n6'))
            self.assertGreaterEqual(k, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Name NOT IN ('PEG n7', 'PEG n6')")
            for m, item in enumerate(items):
                self.assertTrue(item.GetValue("Name") not in ('PEG n7', 'PEG n6'))
            self.assertGreaterEqual(m, 0)
    
    
    def test_read_query_and(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts > 1 AND NumberOfAdducts < 3")
            for i, item in enumerate(items):
                self.assertEqual(item.GetValue("NumberOfAdducts"), 2)
            self.assertGreaterEqual(i, 0)
    
    
    def test_read_query_or(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="NumberOfAdducts = 1 OR NumberOfAdducts = 2")
            for i, item in enumerate(items):
                self.assertTrue(item.GetValue("NumberOfAdducts") in (1, 2))
            self.assertGreaterEqual(i, 0)
    
    
    def test_read_query_group(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="Name LIKE 'PEG%' AND (NumberOfAdducts = 1 OR NumberOfAdducts = 2)")
            for i, item in enumerate(items):
                self.assertTrue(item.GetValue("Name").startswith("PEG"))
                self.assertTrue(item.GetValue("NumberOfAdducts") in (1, 2))
            self.assertGreaterEqual(i, 0)
    
    
    def test_read_query_null(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="AnnotationMolecularWeight IS NULL")
            for i, item in enumerate(items):
                self.assertIsNone(item.GetValue("AnnotationMolecularWeight"))
            self.assertGreaterEqual(i, 0)
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="AnnotationMolecularWeight IS NOT NULL")
            for j, item in enumerate(items):
                self.assertIsNotNone(item.GetValue("AnnotationMolecularWeight"))
            self.assertGreaterEqual(j, 0)
    
    
    def test_read_query_order(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="ORDER BY MaxArea")
            last = 0
            for i, item in enumerate(items):
                if i == 100: break
                value = item.GetValue("MaxArea")
                self.assertGreaterEqual(value, last)
                last = value
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="ORDER BY 'Area (Max.)'")
            last = 0
            for i, item in enumerate(items):
                if i == 100: break
                value = item.GetValue("Area (Max.)")
                self.assertGreaterEqual(value, last)
                last = value
    
    
    def test_read_query_order_desc(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="ORDER BY MaxArea DESC")
            last = float("inf")
            for i, item in enumerate(items):
                if i == 100: break
                value = item.GetValue("MaxArea")
                self.assertLessEqual(value, last)
                last = value
            
            items = eds.Read("ConsolidatedUnknownCompoundItem", query="ORDER BY 'Area (Max.)' DESC")
            last = float("inf")
            for i, item in enumerate(items):
                if i == 100: break
                value = item.GetValue("Area (Max.)")
                self.assertLessEqual(value, last)
                last = value
    
    
    def test_read_query_limit(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items15 = list(eds.Read("ConsolidatedUnknownCompoundItem", query="LIMIT 5"))
            self.assertEqual(len(items15), 5)
    
    
    def test_read_query_limit_offset(self):
        """Tests whether Read works correctly."""
        
        with pyeds.EDS(self.result_file) as eds:
            
            items15 = list(eds.Read("ConsolidatedUnknownCompoundItem", query="LIMIT 5"))
            
            items35 = list(eds.Read("ConsolidatedUnknownCompoundItem", query="LIMIT 3 OFFSET 2"))
            self.assertEqual(len(items35), 3)
            self.assertEqual(items35[0].ID, items15[2].ID)
            self.assertEqual(items35[1].ID, items15[3].ID)
            self.assertEqual(items35[2].ID, items15[4].ID)


# run test case
if __name__ == "__main__":
    unittest.main(verbosity=2)
