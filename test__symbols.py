#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Yuta Hayashibe' 
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"

import random
import unittest

import codecs
import symbols

#ignore_contained_symbols = [1]

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_replacement(self):
        self.tests = [[]]
        for line in codecs.open(u"test.txt", u"r", u"utf8"):
            line = line.lstrip().rstrip()
#            波ダッシュ(U+301C)を全角チルダ(U+FF5E)に変更
            line = line.replace(u"\u301C", u"\uFF5E")

            if len(line)!=0 and not line.startswith(u"#"):
                items = line.split(u"\t")
                if len(items) != 3:
                    continue
                if len(self.tests[-1]) == 3:
                    self.tests[-1] += items[1:]
                else:
                    self.tests.append(items[0:])
        del self.tests[0]

        for (contained_symbols, eng, jpn, gold_new_eng, gold_new_jpn) in self.tests:
            new_eng, new_jpn, isOK = symbols.getReplaced(eng, jpn)
            print "--"
            print contained_symbols
            print "", eng, jpn
            print ">>", new_eng, new_jpn
            print "Gold>>", gold_new_eng, gold_new_jpn
            print "OK?", isOK
            if isOK:
                self.assertEqual(new_eng, gold_new_eng)
                self.assertEqual(new_jpn, gold_new_jpn)


    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
