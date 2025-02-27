import unittest
from sql2tsv import read_string, read_value, read_values, read_all_values, read_sql
from io import StringIO

class TestSql2Tsv(unittest.TestCase):
    def test_read_string(self):
        """Test for read_string function"""
        src = r"'a,b','c\'d'"
        
        # First string
        result = read_string(src, 0)
        self.assertIsNotNone(result)
        s, pos = result
        self.assertEqual(s, "a,b")
        self.assertEqual(pos, 5)
        
        # Second string
        result = read_string(src, 6)
        self.assertIsNotNone(result)
        s, pos = result
        self.assertEqual(s, "c'd")
        self.assertEqual(pos, 12)
    
    def test_read_value(self):
        """Test for read_value function"""
        # Test with non-string values
        src = "1,2,3"
        result = read_value(src, 0)
        self.assertIsNotNone(result)
        s, pos = result
        self.assertEqual(s, "1")
        self.assertEqual(pos, 1)
        
        result = read_value(src, 2)
        self.assertIsNotNone(result)
        s, pos = result
        self.assertEqual(s, "2")
        self.assertEqual(pos, 3)
        
        result = read_value(src, 4)
        self.assertIsNotNone(result)
        s, pos = result
        self.assertEqual(s, "3")
        self.assertEqual(pos, 5)
        
        # Test with string values
        src = r"1,'a,b','c\'d'"
        result = read_value(src, 0)
        self.assertIsNotNone(result)
        s, pos = result
        self.assertEqual(s, "1")
        self.assertEqual(pos, 1)
        
        result = read_value(src, 2)
        self.assertIsNotNone(result)
        s, pos = result
        self.assertEqual(s, "a,b")
        self.assertEqual(pos, 7)
        
        result = read_value(src, 8)
        self.assertIsNotNone(result)
        s, pos = result
        self.assertEqual(s, "c'd")
        self.assertEqual(pos, 14)
    
    def test_read_values(self):
        """Test for read_values function"""
        # Test with non-string values
        src = "(1,2,3)"
        result = read_values(src, 0)
        self.assertIsNotNone(result)
        values, pos = result
        self.assertEqual(values, ["1", "2", "3"])
        self.assertEqual(pos, 7)
        
        # Test with string values
        src = r"(1,'a,b','c\'d')"
        result = read_values(src, 0)
        self.assertIsNotNone(result)
        values, pos = result
        self.assertEqual(values, ["1", "a,b", "c'd"])
        self.assertEqual(pos, 16)
    
    def test_read_all_values(self):
        """Test for read_all_values function"""
        src = r"(1,2,3),(1,'a,b','c\'d')"
        values = read_all_values(src, 0)
        self.assertEqual(values, [["1", "2", "3"], ["1", "a,b", "c'd"]])
    
    def test_read_sql(self):
        """Test for read_sql function"""
        # Using customized test cases
        src = """
INSERT INTO `table` VALUES (1,2,3),(4,5,6);
INSERT INTO `table` VALUES (1,'a,b','c\\'d');
""".strip()
        
        print(f"Debug - Test SQL: {repr(src)}")
        
        stream = StringIO(src)
        results = list(read_sql(stream))
        print(f"Debug - read_sql results: {results}")
        
        self.assertEqual(len(results), 3)
        
        table1, values1 = results[0]
        self.assertEqual(table1, "table")
        self.assertEqual(values1, ["1", "2", "3"])
        
        table2, values2 = results[1]
        self.assertEqual(table2, "table")
        self.assertEqual(values2, ["4", "5", "6"])
        
        table3, values3 = results[2]
        print(f"Debug - values3: {values3}")
        self.assertEqual(table3, "table")
        self.assertEqual(values3, ["1", "a,b", "c'd"])

if __name__ == "__main__":
    unittest.main()
