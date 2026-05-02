# 単語リストから発音音声を作成する手順

この手順は、[Law/18words.md](Law/18words.md) のように `<summary>単語</summary>` が並んだ単語リストから、発音練習用の MP3 を作る方法です。

## 1. 前提コマンドの確認

macOS 標準の `say` と、MP3 変換用の `ffmpeg` を使います。

```bash
command -v say
command -v ffmpeg
```

`ffmpeg` がない場合はインストールします。

```bash
brew install ffmpeg
```

## 2. 単語を抽出する

以下は [Law/18words.md](Law/18words.md) から単語だけを順番通りに取り出す例です。

```bash
grep -o '<summary>.*</summary>' Law/18words.md \
| sed -E 's#<summary>(.*)</summary>#\1#' \
> Law/18words_words.txt
```

## 3. 読み上げ用テキストを作る

単語の間に少し間を作るため、末尾に `...` を付けます。

```bash
awk '{print $0 "..."}' Law/18words_words.txt > Law/18words_tts_script.txt
```

## 4. 音声を生成する

`say` で AIFF を作成します。声は好みで変更できます（例: `Samantha`, `Alex`）。

```bash
say -v Samantha -f Law/18words_tts_script.txt -o Law/18words.aiff
```

## 5. MP3 に変換する

```bash
ffmpeg -y -i Law/18words.aiff -codec:a libmp3lame -b:a 128k Law/18words.mp3
```

## 6. 出力確認

```bash
ls -lh Law/18words.mp3
afinfo Law/18words.mp3 | head -n 20
```

## 7. 1コマンドで実行する例

```bash
grep -o '<summary>.*</summary>' Law/18words.md \
| sed -E 's#<summary>(.*)</summary>#\1#' \
> Law/18words_words.txt \
&& awk '{print $0 "..."}' Law/18words_words.txt > Law/18words_tts_script.txt \
&& say -v Samantha -f Law/18words_tts_script.txt -o Law/18words.aiff \
&& ffmpeg -y -i Law/18words.aiff -codec:a libmp3lame -b:a 128k Law/18words.mp3
```

## 補足

- 発音速度を落としたい場合: `say` 実行時に `-r 160` のように読み上げ速度を指定できます。
- 間隔をさらに空けたい場合: `awk` の `"..."` を `"......"` に増やします。
- 他ファイルに適用する場合: `Law/18words` の部分を対象パスに置き換えてください。