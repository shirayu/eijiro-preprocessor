#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
特殊記号を置換するスクリプト
"""

__author__ = 'Yuta Hayashibe' 
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"


import sys
import optparse
import codecs


"""
@0 ～ [~__-]    第1スロット
    "～"は全角チルダ(U+FF5E)で，波ダッシュ(U+301C)とは区別すること
@1 … (末尾に省略)   第2スロット
@2 ＿   数字が入る
    ＿月＿日という用例も有る．．
@3 （人）someone's
@4 （人）someone
@5      one's
@6      be動詞
@7      oneself
"""

def replace2(eng, jpn):
    new_eng, new_jpn = eng, jpn

    position_jpn_symbol1 = jpn.find(u"＿")
    if position_jpn_symbol1 != -1:
        new_jpn = new_jpn[:position_jpn_symbol1] + u"@2" + new_jpn[position_jpn_symbol1+1:]

        #英訳に__を含む場合はそれがシンボル
        position_eng_symbol1 = eng.find(u"__")
        if position_eng_symbol1 != -1:
            new_eng = new_eng[:position_eng_symbol1] + u"@2" + new_eng[position_eng_symbol1+2:]
            return new_eng, new_jpn

        #接尾辞的に使われる -fold worse
        if new_eng.startswith(u"-"):
            new_eng = u"@2" + new_eng
            return new_eng, new_jpn

        #どれでも無いなら，英訳で末尾の~が省略されている
        new_eng = new_eng + u" @2"
    return new_eng, new_jpn


#～, @0
def replace0(eng, jpn):
    new_eng, new_jpn = eng, jpn

    position_jpn_symbol1 = jpn.find(u"～")
    if position_jpn_symbol1 != -1:
        #symbol2の検査後，英訳に__を含む場合，
        #日本語の〜と，英語の__が実は対応している
        position_eng_symbol1 = eng.find(u"__")
        if position_eng_symbol1 != -1:
            new_jpn = new_jpn[:position_jpn_symbol1] + u"@2" + new_jpn[position_jpn_symbol1+1:]
            new_eng = new_eng[:position_eng_symbol1] + u"@2" + new_eng[position_eng_symbol1+2:]
            return new_eng, new_jpn

        #日本語の〜と，英語のone'sが実は対応している
        if u"…" in jpn:
            position_eng_symbol1 = eng.find(u" one's ")
            if position_eng_symbol1 != -1:
                new_jpn = new_jpn[:position_jpn_symbol1] + u"@5" + new_jpn[position_jpn_symbol1+1:]
                new_eng = new_eng[:position_eng_symbol1] + u" @5 " + new_eng[position_eng_symbol1+7:]
                return new_eng, new_jpn


        new_jpn = new_jpn[:position_jpn_symbol1] + u"@0" + new_jpn[position_jpn_symbol1+1:]

        #英訳に~を含む場合はそれがシンボル
        position_eng_symbol1 = eng.find(u"~")
        if position_eng_symbol1 != -1:
            new_eng = new_eng[:position_eng_symbol1] + u"@0" + new_eng[position_eng_symbol1+1:]
            return new_eng, new_jpn

        #英訳に"__"が<まだ>残っている場合はそれがシンボル
        position_eng_symbol1 = eng.find(u"__")
        if position_eng_symbol1 != -1:
            new_eng = new_eng[:position_eng_symbol1] + u"@0" + new_eng[position_eng_symbol1+2:]
            return new_eng, new_jpn

        #-based 等の接尾辞
        if new_eng.startswith(u"-"):
            new_eng = u"@0" + new_eng
            return new_eng, new_jpn

        #どれでも無いなら，英訳で末尾の~が省略されている
        new_eng = new_eng + u" @0"
    return new_eng, new_jpn


#…, @1
def replace1(eng, jpn):
    new_eng, new_jpn = eng, jpn

    position_jpn_symbol1 = jpn.find(u"…")
    if position_jpn_symbol1 != -1:
        new_jpn = new_jpn[:position_jpn_symbol1] + u"@1" + new_jpn[position_jpn_symbol1+1:]

        #どれでも無いなら，英訳で末尾の~が省略されている
        new_eng = new_eng + u" @1"
    return new_eng, new_jpn


#（人）, @3
def replace3(eng, jpn):
    new_eng, new_jpn = eng, jpn

    position_jpn_symbol1 = jpn.find(u"（人）")
    if position_jpn_symbol1 != -1:

        #---someone's
        position_eng_symbol1 = eng.find(u"someone's")
        if position_eng_symbol1 != -1:
            new_eng = new_eng.replace(u"someone's", u"@3", 1)
            new_jpn = new_jpn.replace(u"（人）", u"@3", 1)
            return new_eng, new_jpn

        #---someone
        new_jpn = new_jpn.replace(u"（人）", u"@4", 1)
        position_eng_symbol1 = eng.find(u"someone")
        if position_eng_symbol1 != -1:
            new_eng = new_eng.replace(u"someone", u"@4", 1)
            return new_eng, new_jpn

        #どれでも無いなら，英訳で末尾
        new_eng = new_eng + u" @4"
    return new_eng, new_jpn

def continEnglishSymbol(eng):
    for k in [u"__", u"~", u"someone", u"someone's", u"one's"]:
        if k in eng:
            return True
    return False


def isOK(jpn, eng):
    for k in [u"＿", u"～"]:
        if k in jpn:
            return False
        
    if continEnglishSymbol(eng):
        return False

    return True
 
def number9(jpn, eng):
    return (u"…" in jpn) and (u"～" in jpn) and \
            (not continEnglishSymbol(eng))
    
def number17(jpn, eng):
    return (u"…" not in jpn) and (u"～" in jpn) and \
            (u"＿" in jpn) and \
            (not continEnglishSymbol(eng))


TARGET_SYMBOLS = [
        u"～", u"~", u"-",
        u"…",
        u"＿",
        u"__",
        u" someone's ",
        u" someone ",
        u" one's ",
        u" oneself ",
]
def getPatternNumber(eng, jpn):
    contained_symbols = 0
    for i, target_symbol in enumerate(TARGET_SYMBOLS):
        if target_symbol in eng or target_symbol in jpn:
            val = 1 << i
            contained_symbols += val
    return contained_symbols



def getReplaced(eng, jpn):
    new_eng, new_jpn = eng, jpn
    new_eng, new_jpn = replace2(new_eng, new_jpn)
    new_eng, new_jpn = replace0(new_eng, new_jpn)
    new_eng, new_jpn = replace1(new_eng, new_jpn)
    new_eng, new_jpn = replace3(new_eng, new_jpn)
    if new_eng.find(u"someone's") != -1:
        return new_eng, new_jpn, False
    new_eng = new_eng.replace(u"one's", u"@5")
    new_eng = new_eng.replace(u"oneself", u"@7")

    contained_symbols = getPatternNumber(eng, jpn)
    if contained_symbols in [9, 17, 21, 137]:
        return new_eng, new_jpn, False


    return new_eng, new_jpn, isOK(new_jpn, new_eng)


