# TOEFL 頻出単語クイズ - プロジェクト概要

## 全体構成

本プロジェクトは **頻出単語クイズ**を提供する静的 Web アプリケーションです。

### 必要なファイル構成

```
toefl/
├── quiz/
│   └── index.html                 # クイズページ（GitHub Pages で公開）
├── data/
│   └── word_frequency.json        # 頻度ランキングデータ（自動生成）
├── scripts/
│   └── generate_frequency_data.py # 集計スクリプト
└── [Subject]/                     # 各科目フォルダ
    ├── NN_words.md                # 単語定義ファイル
    └── NN_pronunciation/
        └── audio/
            └── NNN_word.mp3       # 上位100の単語音声ファイルのみ
```

### GitHub Pages での公開方法

1. リポジトリの **Settings** → **Pages** を開く
2. **Build and deployment** で以下を設定：
   - Source: `Deploy from a branch`
   - Branch: `main` / `root`
3. URL: `https://[username].github.io/toefl/quiz/index.html`

---

## 頻出単語クイズ機能

### 概要

複数の単語集に繰り返し出現する単語を自動集計し、頻出順に学習できるクイズです。

### クイズの特徴

#### 出題モード（3種類）
- **頻出順**：出現回数が多い順に出題
- **ランダム**：ランダムな順序で出題
- **復習**：間違えた単語だけを出題

#### フィルタ機能
- 科目別フィルタ：特定の科目のみに絞り込み可能
- 問題数選択：10/20/30/50/100 問から選択可能

#### UI 機能
- **🔊 音声再生ボタン**：上位100の単語は音声再生可能
- **頻出ランキング**：折りたたみ可能なランキング表示
  - クイズ中は非表示（回答を見やすく）
  - クリックで展開・収納可能

#### 成績管理
- **localStorage** に正解数・不正解数を自動保存
- ページを閉じても履歴が保持される

#### GitHub Pages 対応
- 相対パスのみを使用（バックエンド不要）
- リポジトリ配下の公開に対応

---

## 更新・運用手順

### 単語を追加してクイズを更新する場合

#### ステップ 1. 単語をマークダウンファイルに追加

```bash
# 例：生物学の単語を追加
vim Biology/37words.md
```

既存の形式に合わせて記入してください。

#### ステップ 2. 音声ファイルを追加（オプション）

**方法 A：自動生成（推奨）**

スクリプトが不足している音声を Google TTS で自動生成できます。

```bash
# 1. gTTS をインストール
python3 -m pip install gtts

# 2. スクリプトを実行
cd /Users/tokuhisa/git/toefl
python3 scripts/generate_frequency_data.py
```

スクリプトが自動で以下を行います：
- 上位100位内の単語で音声が不足している箇所を検出
- Google TTS で音声を生成
- 正しいフォルダ・ファイル名で自動配置
- JSON を更新

**出力例：**
```
=== Audio File Management ===
Top 100 words: 100
Audio files kept: 66
Audio files generated: 34  ✅ 新たに生成された音声数
```

#### ステップ 3. 集計スクリプトを実行

```bash
cd /Users/tokuhisa/git/toefl

# 初回のみ：gTTS ライブラリをインストール
python3 -m pip install gtts

# スクリプト実行（毎回）
python3 scripts/generate_frequency_data.py
```

**スクリプトが自動で以下を実行します：**
- 全科目の単語を集計 → 頻度ランキング生成
- 上位100位の単語を特定
- 不足している音声ファイルを自動生成（Google TTS）
- 生成されたファイルを自動検出・JSON に登録
- 不要な音声ファイルを削除（容量削減）

**出力例：**
```
Wrote data/word_frequency.json
Wrote data/word_frequency.tsv
Entries: 2924
Unique words: 2486

=== Audio File Management ===
Top 100 words: 100
Audio files kept: 100
Audio files removed: 0
Audio files generated: 34 (新しく生成)

✅ All top 100 words have audio files!
```

#### ステップ 4. GitHub に変更をプッシュ

```bash
git add .
git commit -m "Update word frequency and audio files (top 100)"
git push origin main
```

#### ステップ 5. ブラウザでクイズを確認

- `https://[username].github.io/toefl/quiz/index.html` を開く
- 新しい単語が反映されているか確認

---

## 技術仕様

### データ生成スクリプト（`scripts/generate_frequency_data.py`）

| 機能 | 説明 |
|------|------|
| **入力** | 全科目の `NN_words.md` ファイル |
| **処理** | 単語を正規化し、重複を集計 |
| **出力** | `data/word_frequency.json` |
| **音声管理** | 上位100の単語のみ音声ファイルを保持、他は削除 |

### JSON スキーマ（`data/word_frequency.json`）

```json
{
  "generated_at": "2026-06-22T...",
  "unique_word_count": 2486,
  "items": [
    {
      "rank": 1,
      "word": "certain",
      "normalized_word": "certain",
      "count": 6,
      "subjects": ["Biology", "Medicine"],
      "files": ["Biology/37words.md", "Medicine/56words.md"],
      "audio_path": "Biology/37words_pronunciation/audio/046_certain.mp3",
      "meaning": "ある；特定の；確かな",
      ...
    }
  ]
}
```

### ローカルテスト

```bash
# HTTP サーバーを起動
cd /Users/tokuhisa/git/toefl
python3 -m http.server 8000

# ブラウザで開く
open http://localhost:8000/quiz/index.html
```

---

## よくある質問

### Q. 音声ファイルがない単語はどうなる？
A. 🔊 ボタンが表示されず、テキストベースでクイズが出題されます。エラーは発生しません。

### Q. 上位100位以外の単語は削除される？
A. ランキングには出現しますが、音声ファイルのみが削除されます。単語そのものは保持されます。

### Q. localStorage の履歴は引き継がれる？
A. はい。スクリプト実行後もブラウザの履歴は保持されます。

### Q. リポジトリ配下のパスで公開できる？
A. はい。相対パスのみを使用しているため、`https://domain.com/repo-name/quiz/index.html` でも動作します。

### Q. スクリプト実行時に gTTS エラーが出る
A. 以下のコマンドで gTTS を再インストール：
```bash
python3 -m pip install --upgrade gtts
```

### Q. インターネット接続なしで音声生成できる？
A. いいえ。gTTS は Google Translate API を利用するため、インターネット接続が必須です。

### Q. 音声生成をスキップしたい
A. `generate_frequency_data.py` を実行すると自動生成されます。  
既存の音声ファイルを残したい場合は、スクリプト内の `generate_missing_audio()` 関数呼び出しをコメントアウトしてください。

### Q. 手動で音声ファイルを追加してから実行したい
A. ファイルを正しいフォルダに配置してからスクリプトを実行すれば、自動で検出・登録されます：
```
SantaAI/SantaAI_pronunciation/audio/005_confirm.mp3
Ethnology/Ethnology_pronunciation/audio/020_interact.mp3
```