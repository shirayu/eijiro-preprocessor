#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
英辞郎の変換．
"""

__author__ = 'Yuta Hayashibe' 
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"


import sys
import optparse
import codecs
import json


SEPARATER = u' : '
FIRSRT = u'■'
POS_START = u'{'
POS_END = u'}'
MEMO_START = u'◆'
SAMPLE_START = u'■・'
TRANS_SEPARATER = u'、'

import re
HOWTOREAD  = re.compile(u"｛[^｝]*｝")
REPRACES  = re.compile(u"［[^］]*］")
LABEL  = re.compile(u"([〔【《〈][^〉》】〕]*[〉》】〕])")


import symbols


def getLabels(trans):
    """語釈文からラベルを抽出する"""
    assert isinstance(trans, unicode)

    result = LABEL.search(trans)
    if result:
        trans = re.sub(LABEL, r'', trans)
        return trans, result.groups()
    return trans, []


def addTrans(translations, line, prev, i):
    """翻訳を追加する"""
    original_trans = line[prev:i]
    trans = re.sub(HOWTOREAD, r'', original_trans) #remove how to read
    trans = re.sub(REPRACES, r'', trans)
    _trans, labels = getLabels(trans)
    translations.append({u"translation":_trans, u"labels":labels})

def lineparse(line):
    if line[0] != FIRSRT:
        raise
    line_length = len(line)

    #Get POS & entry
    pos = None
    entry_pos = line.find(SEPARATER)
    if line[entry_pos-1] == POS_END:
        trans_start = line.find(POS_START)
        entry = line[1:trans_start-1].rstrip()

        #POS
        pos = line[trans_start+1:entry_pos-1]
        __pos = pos.split(u"-")
        if __pos[0].isdigit():
            if len(__pos) >= 2:
                pos = __pos[1]
            else:
                pos = None
        else:
            pos = __pos[0]
    else:
        entry = line[1:entry_pos].rstrip()

#    memo_pos = line.find(MEMO_START)
    sample_pos = line.find(SAMPLE_START)

    #Get translation
    translations = []
    memo = None
    samples = []

    i = entry_pos + len(SEPARATER)
    prev = i
    memo_done = False
    while True:
        if i >= line_length:
            addTrans(translations, line, prev, i)
            break
        elif line[i] == MEMO_START:
            memo_done = True
            addTrans(translations, line, prev, i)
            if sample_pos == -1:
                tail = line_length
            else: # this line has sample(s)
                tail = sample_pos
            memo = line[i+1:tail]
            memo = re.sub(HOWTOREAD, r'', memo) #remove how to read
            i = tail
            if sample_pos == -1:
                break
        elif i == sample_pos:
            if not memo_done:
                addTrans(translations, line, prev, i)
            prev = sample_pos
            while prev < line_length:
                next_sample_pos = line.find(SAMPLE_START, prev+1)
                if next_sample_pos == -1:
                    next_sample_pos = line_length + 1
                sample = line[prev+len(SAMPLE_START) : next_sample_pos]
                sample = re.sub(HOWTOREAD, r'', sample) #remove how to read
                samples.append(sample)
                prev = next_sample_pos
            break
        elif line[i] == TRANS_SEPARATER:
            addTrans(translations, line, prev, i)
            prev = i+1
            i += 1
        else:
            i += 1

    return entry, pos, translations, memo, samples


def out2file(fpointer, outdic):
    outstring = json.dumps(outdic, ensure_ascii=False)
    fpointer.write(outstring)
    fpointer.write("\n")


def convert(ifname, ofname):
    f_out_word = codecs.open( ofname+'word.jsons' , 'w', 'utf8')
    f_out_phrase = codecs.open( ofname+'phrase.jsons' , 'w', 'utf8')


    f  = codecs.open(opts.ifname, 'r', opts.encode)
    prev_word_entry = None
    wordid = 0 #TODO suppose the order is fixed?
    phraseid = 0
    words = {}

    prev_line = None
    for lid, line in enumerate(f):
        if line == prev_line:
            continue
        prev_line = line #renew

        if lid % 10000 == 0:
            sys.stderr.write("\r%10d" % lid)

        entry, pos, translations, memo, samples = lineparse(line.rstrip())
        if memo is None:
            memo = "-"

        #TODO how abotu 'acrylyl group' ???
        if (pos is not None): #品詞がある = 単語だと断定
            #前のエントリと同じ
#            if (prev_word_entry == entry):
                #'samples' には単語に関する情報が詰まっている
#                words[entry][u"info"][-1][u"samples"] += samples
#            else:
            if prev_word_entry is not None\
                    and (prev_word_entry != entry):
                out2file(f_out_word, words[prev_word_entry])

            if (entry not in words):
                wordid += 1
                words[entry] = {u"wordid" : wordid, u"entry" : entry, u"info":[]}


            info = {u"pos" : pos, u"translations" : translations, u"memo" : memo, u"samples":samples}
            words[entry][u"info"].append(info)
            prev_word_entry = entry


        #FIXME 「パターン」または「フレーズ」
        else:
            phraseid += 1

            eng = entry
            jpn = translations[0][u"translation"] #第1翻訳を使用

            #ラベルの処理
            labels = translations[0][u"labels"] #第1翻訳のラベルを使用
            if u"《one's ～》" in labels:
                eng = u"one's " + eng
            if u"《someone's ～》" in labels:
                eng = u"someone's " + eng

            new_eng, new_jpn, isOK = symbols.getReplaced(eng, jpn)

            outdic = {u"phraseid" : phraseid,
                    u"entry" : entry,
                    u"translations" : translations,
                    u"error" : not isOK,
                    u"eng" : new_eng,
                    u"jpn" : new_jpn,
                    u"labels" : labels,
                    u"memo" : memo,
                    u"samples" : samples,
                    }
            out2file(f_out_phrase, outdic)


def __checkarg(opts):
    error = False
    mandatories = [ (opts.ifname, "[ERROR] Designate the input file name"), \
        (opts.ofname, "[ERROR] Designate the output file name") ]

    for (k, v) in mandatories:
        if not k:
            sys.stderr.write(v)
            sys.stderr.write("\n")
            error = True

    if error:
        quit(-1)



if __name__ == "__main__":
    argvs = sys.argv
    argc = len(argvs)
    INCODE = 'utf-8'


    parser = optparse.OptionParser(usage="%prog filename", version="%prog 1.0")
    parser.add_option('-i', '--in', dest = 'ifname')
    parser.add_option('-o', '--out', dest = 'ofname')
    parser.add_option("-e", '--encode', dest="encode", default='cp932')

    (opts, args) = parser.parse_args()
    __checkarg(opts)

    convert(opts.ifname, opts.ofname)


