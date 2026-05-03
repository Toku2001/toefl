# 単語リストから発音音声を作成する手順

この手順は、[Law/18words.md](Law/18words.md) のように `<summary>単語</summary>` が並ぶファイルから、
1単語ずつの発音 MP3 と、クリック表示できるページを作成する方法です。

## 単語リストのフォーマット

`<details>` ブロック内に以下の情報を記載してください。

```html
<details>
<summary>単語</summary>

**意味:** 意味の説明

**アクセント:** ə-**MĔND**

**類義語:** 類似表現, 同義語, など

</details>
```

- **意味:** は必須です。
- **基本形:** （オプション）不規則変化の場合に記載します。
- **アクセント:** （オプション）単語の発音記号です。
- **類義語:** （オプション）類似語や同義語です。

スクリプトはこれらすべての行を抽出し、クリック時に表示させます。

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

- `Law/pronunciation/index.html` : 単語クリック・意味表示ページ
- `Law/pronunciation/audio/*.mp3` : 単語ごとの音声ファイル
- `Law/pronunciation/words.txt` : 抽出した単語一覧
- `Law/pronunciation/word_map.tsv` : 単語と音声ファイルの対応表
- `Law/pronunciation/word_meanings.tsv` : 単語と詳細情報（意味・アクセント・類義語など）の対応

## 4. 再生ページを開く

```bash
open Law/pronunciation/index.html
```

ページ内で、各単語を押すと意味を表示します。Play ボタンを押すと発音のみ再生されます。

## 5. 読み上げ音声や速度を変更する

環境変数で声と速度を変更できます。

```bash
VOICE=Alex RATE=160 bash Law/generate_word_audio_and_html.sh Law/18words.md Law/pronunciation
```

- `VOICE` 例: `Samantha`, 

## 5.5 既存の音声を使ってページだけ再生成する

`SKIP_AUDIO=1` を指定すると、音声生成をスキップしてHTMLだけ更新できます。言葉の説明を修正したときに便利です。

```bash
SKIP_AUDIO=1 bash Law/generate_word_audio_and_html.sh Law/18words.md Law/pronunciation
```

既に存在する MP3 ファイルを再利用し、新しい `index.html` が生成されます。`Alex`
- `RATE` は読み上げ速度（大きいほど速い）

## 6. 他の単語ファイルへ適用する

入力ファイルと出力フォルダを変更すれば、同じ手順を流用できます。

```bash
bash Law/generate_word_audio_and_html.sh History/07words.md History/07words_pronunciation
```

## 7. 複数のフォルダを一括更新する

すべての単語ファイル用の発音ページを更新する場合は、以下スクリプトを実行します。

```bash
for src in AmericanHistory/06words.md AmericanHistory/08words.md History/07words.md Law/18words.md; do
  out_dir=${src%.md}_pronunciation
  SKIP_AUDIO=1 bash Law/generate_word_audio_and_html.sh "$src" "$out_dir"
done
```

## 8. README にプレビューリンクを追記する（運用ルール）

今後、新しい音声ページを作成したら、`README.md` の「発音プレビュー一覧（番号連動）」に必ず追記します。

- 追記する情報: 番号 / 元ファイル（`xxwords.md`） / `index.html` のリンク
- 例: `14words.md` を作成した場合は、対応する `14words_pronunciation/index.html` を表に追加する

これにより、README から番号ベースで各プレビューをすぐ開ける状態を維持できます。

## 9. 単語の意味情報を修正したときの更新手順

`words.md` の意味、アクセント、類義語を修正した場合は、以下で HTML だけ再生成してください。

```bash
SKIP_AUDIO=1 bash Law/generate_word_audio_and_html.sh Law/18words.md Law/pronunciation
```

この場合、既存の MP3 ファイルは変わらず、`word_meanings.tsv` と `index.html` だけが更新されます。