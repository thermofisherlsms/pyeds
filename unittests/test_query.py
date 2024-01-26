#  Created by Martin Strohalm, Thermo Fisher Scientific

import unittest
import pyeds


class TestCase(unittest.TestCase):
    """Test case for pyeds.EDSQuery class."""
    
    
    def test_equals(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("Column = 2").parse()
        self.assertEqual(query['constraint'], "Column = ?")
        self.assertEqual(query['values'], ['2'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column != 2").parse()
        self.assertEqual(query['constraint'], "Column != ?")
        self.assertEqual(query['values'], ['2'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
    
    
    def test_range(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("Column < 2").parse()
        self.assertEqual(query['constraint'], "Column < ?")
        self.assertEqual(query['values'], ['2'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column <= 2").parse()
        self.assertEqual(query['constraint'], "Column <= ?")
        self.assertEqual(query['values'], ['2'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column > 2").parse()
        self.assertEqual(query['constraint'], "Column > ?")
        self.assertEqual(query['values'], ['2'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column >= 2").parse()
        self.assertEqual(query['constraint'], "Column >= ?")
        self.assertEqual(query['values'], ['2'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
    
    
    def test_like(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("Column LIKE %test").parse()
        self.assertEqual(query['constraint'], "Column LIKE ?")
        self.assertEqual(query['values'], ['%test'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column NOT LIKE %test").parse()
        self.assertEqual(query['constraint'], "Column NOT LIKE ?")
        self.assertEqual(query['values'], ['%test'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
    
    
    def test_in(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("Column IN (1, 2, 3)").parse()
        self.assertEqual(query['constraint'], "Column IN (?, ?, ?)")
        self.assertEqual(query['values'], ['1', '2', '3'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column IN (1)").parse()
        self.assertEqual(query['constraint'], "Column IN (?)")
        self.assertEqual(query['values'], ['1'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column IN (1,)").parse()
        self.assertEqual(query['constraint'], "Column IN (?)")
        self.assertEqual(query['values'], ['1'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
    
    
    def test_and(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("Column1 = 1 AND Column2 != 2 AND Column3 IN (3, 4, 5)").parse()
        self.assertEqual(query['constraint'], "Column1 = ? AND Column2 != ? AND Column3 IN (?, ?, ?)")
        self.assertEqual(query['values'], ['1', '2', '3', '4', '5'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
    
    
    def test_or(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("Column1 > 1 OR Column2 < 2 OR Column3 NOT IN (3, 4, 5)").parse()
        self.assertEqual(query['constraint'], "Column1 > ? OR Column2 < ? OR Column3 NOT IN (?, ?, ?)")
        self.assertEqual(query['values'], ['1', '2', '3', '4', '5'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
    
    
    def test_group(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("(Column1 > 1 AND Column2 < 2) OR Column3 NOT IN (3, 4, 5)").parse()
        self.assertEqual(query['constraint'], "( Column1 > ? AND Column2 < ? ) OR Column3 NOT IN (?, ?, ?)")
        self.assertEqual(query['values'], ['1', '2', '3', '4', '5'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column1 > 1 AND (Column2 < 2 OR Column3 NOT IN (3, 4, 5))").parse()
        self.assertEqual(query['constraint'], "Column1 > ? AND ( Column2 < ? OR Column3 NOT IN (?, ?, ?) )")
        self.assertEqual(query['values'], ['1', '2', '3', '4', '5'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
    
    
    def test_null(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("Column IS NULL").parse()
        self.assertEqual(query['constraint'], "Column IS NULL")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column IS NOT NULL").parse()
        self.assertEqual(query['constraint'], "Column IS NOT NULL")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
    
    
    def test_order(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("ORDER BY Column1").parse()
        self.assertEqual(query['constraint'], "")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "ORDER BY Column1")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("ORDER BY Column1 DESC").parse()
        self.assertEqual(query['constraint'], "")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "ORDER BY Column1 DESC")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("ORDER BY Column1 DESC, Column2").parse()
        self.assertEqual(query['constraint'], "")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "ORDER BY Column1 DESC, Column2")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("ORDER BY Column1 DESC, Column2, Column3 DESC").parse()
        self.assertEqual(query['constraint'], "")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "ORDER BY Column1 DESC, Column2, Column3 DESC")
        self.assertEqual(query['limit'], "")
    
    
    def test_limit(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("LIMIT 2").parse()
        self.assertEqual(query['constraint'], "")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "LIMIT 2")
        
        query = pyeds.eds.EDSQuery("OFFSET 3").parse()
        self.assertEqual(query['constraint'], "")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "OFFSET 3")
        
        query = pyeds.eds.EDSQuery("LIMIT 2 OFFSET 3").parse()
        self.assertEqual(query['constraint'], "")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "LIMIT 2 OFFSET 3")
    
    
    def test_complex(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("(Column1 > 1 AND Column2 IN (2, 3, 4)) OR Column3 IS NOT NULL ORDER BY Column4 DESC, Column5 LIMIT 2 OFFSET 3").parse()
        self.assertEqual(query['constraint'], "( Column1 > ? AND Column2 IN (?, ?, ?) ) OR Column3 IS NOT NULL")
        self.assertEqual(query['values'], ['1', '2', '3', '4'])
        self.assertEqual(query['orderby'], "ORDER BY Column4 DESC, Column5")
        self.assertEqual(query['limit'], "LIMIT 2 OFFSET 3")
        
        query = pyeds.eds.EDSQuery("(Column1 > 1 AND Column2 IN (2, 3, 4)) OR Column3 IS NOT NULL ORDER BY Column4 DESC, Column5").parse()
        self.assertEqual(query['constraint'], "( Column1 > ? AND Column2 IN (?, ?, ?) ) OR Column3 IS NOT NULL")
        self.assertEqual(query['values'], ['1', '2', '3', '4'])
        self.assertEqual(query['orderby'], "ORDER BY Column4 DESC, Column5")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("(Column1 > 1 AND Column2 IN (2, 3, 4)) OR Column3 IS NOT NULL LIMIT 2 OFFSET 3").parse()
        self.assertEqual(query['constraint'], "( Column1 > ? AND Column2 IN (?, ?, ?) ) OR Column3 IS NOT NULL")
        self.assertEqual(query['values'], ['1', '2', '3', '4'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "LIMIT 2 OFFSET 3")
        
        query = pyeds.eds.EDSQuery("ORDER BY Column4 DESC, Column5 LIMIT 2 OFFSET 3").parse()
        self.assertEqual(query['constraint'], "")
        self.assertEqual(query['values'], [])
        self.assertEqual(query['orderby'], "ORDER BY Column4 DESC, Column5")
        self.assertEqual(query['limit'], "LIMIT 2 OFFSET 3")
    
    
    def test_chars(self):
        """Tests whether EDSQuery works correctly."""
        
        query = pyeds.eds.EDSQuery("Column1 != 1").parse()
        self.assertEqual(query['constraint'], "Column1 != ?")
        self.assertEqual(query['values'], ['1'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column1 != 1.5").parse()
        self.assertEqual(query['constraint'], "Column1 != ?")
        self.assertEqual(query['values'], ['1.5'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column1 != 1e5").parse()
        self.assertEqual(query['constraint'], "Column1 != ?")
        self.assertEqual(query['values'], ['1e5'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column1 != 'text'").parse()
        self.assertEqual(query['constraint'], "Column1 != ?")
        self.assertEqual(query['values'], ['text'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column1 != 'AZaz09-_%. ()[]+#/:'").parse()
        self.assertEqual(query['constraint'], "Column1 != ?")
        self.assertEqual(query['values'], ['AZaz09-_%. ()[]+#/:'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("Column1 IN ('AZaz09-_%. ()[]+#/:', 2)").parse()
        self.assertEqual(query['constraint'], "Column1 IN (?, ?)")
        self.assertEqual(query['values'], ['AZaz09-_%. ()[]+#/:', '2'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")
        
        query = pyeds.eds.EDSQuery("'Column AZaz09-_. ()[]+#/:' != 1").parse()
        self.assertEqual(query['constraint'], "Column AZaz09-_. ()[]+#/: != ?")
        self.assertEqual(query['values'], ['1'])
        self.assertEqual(query['orderby'], "")
        self.assertEqual(query['limit'], "")


# run test case
if __name__ == "__main__":
    unittest.main(verbosity=2)
