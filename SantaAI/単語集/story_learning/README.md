# 5-Story Vocabulary Learning Pack

3か月分の『知らない単語集』を、5本の連続ストーリー教材に再構成したセットです。

- 元エントリ数: 1699
- ユニーク語彙数: 1384
- 章数: 5

## Files
- story_01.md - story_05.md: 各章の本文（約400語）+ その章の語彙
- vocabulary_coverage.tsv: 1384語の章割り当て一覧

## Regenerate
```bash
cd /Users/tokuhisa/git/toefl
python3 SantaAI/単語集/build_story_learning.py
```

## Daily Use (15-20 min)
1. 1日1章を音読（意味を見ない）
2. 同章の語彙リストを開いて答え合わせ
3. 難しかった語だけノートに10語メモ
4. 翌日は次の章へ進み、6日目に第1章へ戻る