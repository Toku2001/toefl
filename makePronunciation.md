# 単語リストから発音音声を作成する手順

この手順は、[Law/18words.md](Law/18words.md) のように `<summary>単語</summary>` が並ぶファイルから、
1単語ずつの発音 MP3 と、クリック再生できるページを作成する方法です。

## 1. 前提コマンドの確認

macOS の `say` と、MP3 変換用の `ffmpeg` を使用します。

```bash
command -v say
command -v ffmpeg
```

`ffmpeg` が未インストールなら以下を実行します。

```bash
brew install ffmpeg
```

## 2. 生成スクリプトを実行

以下のコマンドで、対象ファイルから単語抽出、単語ごとの MP3 作成、再生ページ生成までを一括実行できます。

```bash
bash Law/generate_word_audio_and_html.sh Law/18words.md Law/pronunciation
```

引数の意味:

- 第1引数: 入力ファイル（例: `Law/18words.md`）
- 第2引数: 出力先ディレクトリ（例: `Law/pronunciation`）

## 3. 生成されるファイル

- `Law/pronunciation/index.html` : 単語クリック再生ページ
- `Law/pronunciation/audio/*.mp3` : 単語ごとの音声ファイル
- `Law/pronunciation/words.txt` : 抽出した単語一覧
- `Law/pronunciation/word_map.tsv` : 単語と音声ファイルの対応表

## 4. 再生ページを開く

```bash
open Law/pronunciation/index.html
```

ページ内で、各単語を押すと発音再生と意味表示、Play ボタンを押すと発音のみ再生されます。

## 5. 読み上げ音声や速度を変更する

環境変数で声と速度を変更できます。

```bash
VOICE=Alex RATE=160 bash Law/generate_word_audio_and_html.sh Law/18words.md Law/pronunciation
```

- `VOICE` 例: `Samantha`, `Alex`
- `RATE` は読み上げ速度（大きいほど速い）

## 6. 他の単語ファイルへ適用する

入力ファイルと出力フォルダを変更すれば、同じ手順を流用できます。

```bash
bash Law/generate_word_audio_and_html.sh History/07words.md History/pronunciation
```

## 7. README にプレビューリンクを追記する（運用ルール）

今後、新しい音声ページを作成したら、`README.md` の「発音プレビュー一覧（番号連動）」に必ず追記します。

- 追記する情報: 番号 / 元ファイル（`xxwords.md`） / `index.html` のリンク
- 例: `14words.md` を作成した場合は、対応する `14words_pronunciation/index.html` を表に追加する

これにより、README から番号ベースで各プレビューをすぐ開ける状態を維持できます。