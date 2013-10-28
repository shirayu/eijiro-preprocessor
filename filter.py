#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
・「言い換え表現」を除外
・「文」を除外
・「ラベル」から有用な情報を抽出
・「動詞句」の場合は，主辞の位置を特定する
・英語表現をトークナイズする
"""

__author__ = 'Yuta Hayashibe' 
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"


import sys
import optparse
import codecs

import re
pattern_jpn_blacket = re.compile(u"（.+）")

def replace_useful_label(labels, eng, jpn):
    new_eng = eng
    new_jpn = jpn
    new_labels = []
    
    for label in labels:
        if label == u"《be ～》":
            new_eng = u"@6 " + new_eng
        elif label == u"《one's ～》":
            pass
        elif label == u"《be a ～》":
            new_eng = u"@6 a " + new_eng
        elif label == u"《be the ～》":
            new_eng = u"@6 the " + new_eng
        elif label == u"《someone's ～》":
            pass
        elif label == u"《～ A and B》":
            if u"@0" in new_eng:
                raise NotImplementedError    #FIXME currently ignore this
            new_eng = new_eng + u" @0 and @1"
            new_jpn = new_jpn.replace(u"AとB", u"@0と@1")


        else: #do nothing
            new_labels.append(label)

    new_eng = new_eng.replace(u"  ", u" ")
    new_jpn = pattern_jpn_blacket.sub(u"", new_jpn)
    return new_labels, new_eng, new_jpn


import MeCab
mecab_tagger = MeCab.Tagger()
import nltk

def getVPHeadPosition(eng, jpn, eng_tokens):

    if eng[0].isupper(): #This should be a part of a sentence
        raise NotImplementedError
    elif len(eng.split()) <= 1:
        raise NotImplementedError


    #the verb of being
    if eng.startswith(u"@6"):
        return 0

    node = mecab_tagger.parseToNode(jpn.encode("utf8"))
    while node:
        if node.next is None:
            break
        node = node.next
    node = node.prev
    jpn_head_pos = unicode(node.feature, "utf8").split(u",")[0]

    if jpn_head_pos == u"名詞":
        return -1

    if jpn_head_pos == u"記号":
        raise NotImplementedError

    if jpn_head_pos not in [u"形容詞", u"動詞", u"助詞", u"助動詞"]:
        #This phrase must not be VP.
        return -1

    #This may be VP. This MUST NOT BE noun!
    for position, token in enumerate(eng_tokens):
        pos = nltk.tag.pos_tag([token])[0][1]
        if pos == u"VB": #verb base-form
            return position
        elif pos.startswith(u"RB"): #adverb
            continue
        elif pos.startswith(u"N"): #noun (actually it's verb)
            return position
        else:
            return -1

    return -1



import json
def filter_out(ifname, ofname, encode, ):
    f_out = codecs.open(ofname + ".jsons", 'w', encode)
    f_out_error = codecs.open(ofname + ".excluded.jsons", 'w', encode)

    f_in  = codecs.open(ifname, 'r', encode)


    for lid, line in enumerate(f_in):
        if lid % 1000 == 0:
            sys.stderr.write("\r%10d" % lid)

        indic = json.loads(line)
        
        if indic[u"error"] == True:
            f_out_error.write(line)
            continue

        eng = indic[u"eng"]
        jpn = indic[u"jpn"]
        labels = indic[u"labels"]

        #remove paraphrase
        if jpn.startswith(u"＝<")   \
                or jpn.startswith(u"<→"):
            f_out_error.write(line)
            continue

        #replace
        try:
            new_labels, new_eng, new_jpn = replace_useful_label(labels, eng, jpn)
        except NotImplementedError:
            f_out_error.write(line)
            continue

        try:
            eng_tokens = nltk.word_tokenize(new_eng)
            VPHeadPosition = getVPHeadPosition(new_eng, new_jpn, eng_tokens)
        except NotImplementedError:
            f_out_error.write(line)
            continue


        #output
        indic[u"new_eng"] = new_eng
        indic[u"new_jpn"] = new_jpn
        indic[u"new_labels"]  = new_labels
        indic[u"VPHeadPosition"]  = VPHeadPosition

        token_string = u" ".join(eng_tokens).replace(u"@ ", u"@")
        indic[u"new_eng_tokenized"]  = token_string
        
        outstring = json.dumps(indic, ensure_ascii=False)
        f_out.write(outstring)
        f_out.write("\n")


import sys
if __name__ == "__main__":
    argvs = sys.argv
    argc = len(argvs)

    parser = optparse.OptionParser(usage="%prog filename", )
    parser.add_option('-i', '--in', dest = 'ifname')
    parser.add_option('-o', '--out', dest = 'ofname')
    parser.add_option("-e", '--encode', dest="encode", default='utf8')

    (opts, args) = parser.parse_args()

    if not opts.ifname or not opts.ofname:
        raise
    filter_out(opts.ifname, opts.ofname, opts.encode, )


