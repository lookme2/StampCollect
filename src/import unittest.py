import unittest
from stamp import Stamp

# Python

class TestStamp(unittest.TestCase):
    def test_stamp_creation(self):
        stamp = Stamp(name="Blue Penny", country="Mauritius", year=1847)
        self.assertEqual(stamp.name, "Blue Penny")
        self.assertEqual(stamp.country, "Mauritius")
        self.assertEqual(stamp.year, 1847)

    def test_stamp_str(self):
        stamp = Stamp(name="Inverted Jenny", country="USA", year=1918)
        self.assertTrue("Inverted Jenny" in str(stamp))
        self.assertTrue("USA" in str(stamp))
        self.assertTrue("1918" in str(stamp))

    def test_stamp_equality(self):
        stamp1 = Stamp(name="Penny Black", country="UK", year=1840)
        stamp2 = Stamp(name="Penny Black", country="UK", year=1840)
        self.assertEqual(stamp1, stamp2)

    def test_invalid_year(self):
        with self.assertRaises(ValueError):
            Stamp(name="Test", country="Testland", year="not_a_year")

if __name__ == "__main__":
    unittest.main()