#  Created by Martin Strohalm, Thermo Fisher Scientific

# run all available tests
if __name__ == "__main__":
    
    import os.path
    import unittest
    
    import pyeds
    
    suite = unittest.TestLoader().discover(os.path.dirname(__file__), pattern='test_*.py')
    unittest.TextTestRunner(verbosity=2).run(suite)
