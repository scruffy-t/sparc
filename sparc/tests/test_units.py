from unittest import TestCase


class UnitsTest(TestCase):

    def test_convertToBaseUnits(self):

        u0 = 't/(a*km)'
        u1 = 't//(a*km)'

        # self.assertEqual(Units.baseConversionFactor(u0), 1.0/(365*24*3600))
        # self.assertEqual(Units.isValid(u1), False)

