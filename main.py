from pytuist.pytuist import TestDir, get_tests

if __name__ == "__main__":
    collected_tests = get_tests()
    print(collected_tests)
