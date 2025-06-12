import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover('unit_test', pattern='test_util.py')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)