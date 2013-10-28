#英辞郎プリプロセッサ

## このソフトウェアについて
- [英辞郎](http://www.eijiro.jp/)を計算機処理しやすい形式に変換するツール
- 英辞郎 version.134で検証

## 使い方

``convert.py``に，英辞郎のファイル名と，出力ファイルのプレフィックスを与えるだけです．

    mkdir outfolder
    python convert.py -i  ~/EIJI-134.TXT -o ./outfolder/eijiro.134.

すると次のようなファイルができます．

- eijiro.134.word.jsons        
- eijiro.134.phrase.jsons      

さらなる後処理が必要ならば，
``MeCab``モジュールと``nltk``モジュールをインストールした後，

    python filter.py -i  ./outfolder/eijiro.134.phrase.jsons -o ./outfolder/eijiro.134.phrase.2

とすることで，``eijiro.134.phrase.2.jsons``という後処理済みファイルができます．
``eijiro.134.phrase.2.excluded.jsons``は除外された行が記録されています．

なお，出力される``.jsons``というファイルには，1行ごとにJSONオブジェクトが書かれています．


## ライセンス
- GPL v3
- Yuta Hayashibe

