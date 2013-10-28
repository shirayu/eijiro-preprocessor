#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
特殊記号の出現パターンを全て網羅したテストファイルを作るためのスクリプト
"""

__author__ = 'Yuta Hayashibe' 
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"


import sys
import optparse
import codecs

import json

import symbols

argvs = sys.argv
argc = len(argvs)
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

examples = {}

pid = 0
for phrase_fname in argvs[1:]:
    with codecs.open(phrase_fname, 'r', "utf8") as f:
        for lid, line in enumerate(f):
            if lid % 1000 == 0:
                sys.stderr.write("\r%10d" % lid)

            pid += 1
            ephrasedic = json.loads(line)
            isError = ephrasedic[u"error"] 

            if not isError:
                jpn = ephrasedic[u"translations"][0][u"translation"]
                eng = ephrasedic[u"entry"] 
                if jpn.startswith(u"＝<")   \
                        or jpn.startswith(u"<→"):
                            pass
                else:
                    contained_symbols = symbols.getPatternNumber(eng, jpn)
                    if contained_symbols not in examples:
                        examples[contained_symbols] = u"%s\t%s" % (eng, jpn)

for (k, v) in examples.items():
    print u"%s\t%s" % (k, v)

