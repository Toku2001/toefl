#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash Law/generate_word_audio_and_html.sh [SOURCE_MD] [OUT_DIR]
# Example:
#   bash Law/generate_word_audio_and_html.sh Law/18words.md Law/pronunciation

SOURCE_MD="${1:-Law/18words.md}"
OUT_DIR="${2:-Law/pronunciation}"
VOICE="${VOICE:-Samantha}"
RATE="${RATE:-170}"
SKIP_AUDIO="${SKIP_AUDIO:-0}"

AUDIO_DIR="$OUT_DIR/audio"
WORDS_FILE="$OUT_DIR/words.txt"
WORD_MEANINGS_FILE="$OUT_DIR/word_meanings.tsv"
MAP_FILE="$OUT_DIR/word_map.tsv"
HTML_FILE="$OUT_DIR/index.html"

if [[ "$SKIP_AUDIO" != "1" ]]; then
  command -v say >/dev/null 2>&1 || { echo "Error: say not found" >&2; exit 1; }
  command -v ffmpeg >/dev/null 2>&1 || { echo "Error: ffmpeg not found" >&2; exit 1; }
fi

mkdir -p "$AUDIO_DIR"

# Always regenerate extracted text files from scratch to avoid stale rows.
: > "$WORDS_FILE"
: > "$WORD_MEANINGS_FILE"

# Detect format: <details>/<summary> block or simple bullet list (- word).
if grep -q '<details>' "$SOURCE_MD"; then
  # Extract word and full detail lines from each <details> block.
  awk -v words_out="$WORDS_FILE" -v pair_out="$WORD_MEANINGS_FILE" '
    BEGIN {
      in_details = 0
      word = ""
      details = ""
    }

    /<details>/ {
      in_details = 1
      word = ""
      details = ""
      next
    }

    in_details && /<summary>/ {
      line = $0
      sub(/^.*<summary>/, "", line)
      sub(/<\/summary>.*$/, "", line)
      word = line
      next
    }

    /<\/details>/ {
      if (in_details && word != "") {
        print word >> words_out
        print word "\t" details >> pair_out
      }
      in_details = 0
      word = ""
      details = ""
      next
    }

    in_details && word != "" {
      line = $0
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
      if (line == "" || line ~ /^<summary>/ || line ~ /<\/summary>/) {
        next
      }

      gsub(/\*\*/, "", line)
      if (details == "") {
        details = line
      } else {
        details = details "\\n" line
      }
    }
  ' "$SOURCE_MD"

  if [[ ! -s "$WORD_MEANINGS_FILE" ]]; then
    echo "Error: no detail lines found in $SOURCE_MD" >&2
    exit 1
  fi
else
  # Simple bullet list format: lines starting with optional spaces then "- " are words.
  awk -v words_out="$WORDS_FILE" -v pair_out="$WORD_MEANINGS_FILE" '
    /^[[:space:]]*- / {
      line = $0
      sub(/^[[:space:]]*- /, "", line)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
      if (line != "") {
        print line >> words_out
        print line "\t" >> pair_out
      }
    }
  ' "$SOURCE_MD"
fi

if [[ ! -s "$WORDS_FILE" ]]; then
  echo "Error: no words found in $SOURCE_MD" >&2
  exit 1
fi

: > "$MAP_FILE"

idx=0
while IFS=$'\t' read -r word details; do
  idx=$((idx + 1))

  # Create a safe slug for file names. Keep letters, numbers and underscores.
  slug=$(echo "$word" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/_/g; s/^_+//; s/_+$//; s/_+/_/g')

  if [[ -z "$slug" ]]; then
    slug="word"
  fi

  base=$(printf "%03d_%s" "$idx" "$slug")
  aiff_path="$AUDIO_DIR/$base.aiff"
  mp3_path="$AUDIO_DIR/$base.mp3"

  # Generate one pronunciation file per word unless skip mode is enabled.
  if [[ "$SKIP_AUDIO" != "1" || ! -f "$mp3_path" ]]; then
    say -v "$VOICE" -r "$RATE" "$word" -o "$aiff_path"
    ffmpeg -y -loglevel error -i "$aiff_path" -codec:a libmp3lame -b:a 128k "$mp3_path"
    rm -f "$aiff_path"
  fi

  printf "%s\t%s\t%s\taudio/%s.mp3\n" "$idx" "$word" "$details" "$base" >> "$MAP_FILE"
done < "$WORD_MEANINGS_FILE"

SOURCE_LABEL=$(basename "$SOURCE_MD")

cat > "$HTML_FILE" <<HTML_HEAD
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${SOURCE_LABEL} Pronunciation</title>
  <style>
    :root {
      --bg1: #f2ece3;
      --bg2: #e4d5c1;
      --card: #fff8ee;
      --ink: #2a1f16;
      --accent: #9a3412;
      --accent-2: #78350f;
      --border: #d9c2a5;
      --shadow: rgba(42, 31, 22, 0.15);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 15% 20%, rgba(255,255,255,0.6), transparent 35%),
        radial-gradient(circle at 85% 80%, rgba(255,255,255,0.4), transparent 30%),
        linear-gradient(135deg, var(--bg1), var(--bg2));
      min-height: 100vh;
      padding: 24px;
    }

    .wrap {
      max-width: 900px;
      margin: 0 auto;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 10px 30px var(--shadow);
    }

    h1 {
      margin: 0 0 8px;
      font-size: clamp(1.5rem, 2.6vw, 2.2rem);
      letter-spacing: 0.02em;
    }

    p {
      margin: 0 0 20px;
      line-height: 1.6;
    }

    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 14px;
    }

    button {
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fff;
      border-radius: 10px;
      padding: 8px 12px;
      font-size: 0.95rem;
      cursor: pointer;
      transition: transform 120ms ease, background 120ms ease;
    }

    button:hover { background: var(--accent-2); }
    button:active { transform: translateY(1px); }

    .word-list {
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 10px;
    }

    .word-item {
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px;
      background: #fff;
      display: grid;
      grid-template-columns: auto 1fr auto;
      align-items: center;
      gap: 8px;
      opacity: 0;
      transform: translateY(8px);
      animation: reveal 360ms ease forwards;
    }

    .play-btn {
      min-width: 56px;
    }

    .word-text {
      background: none;
      border: none;
      color: var(--ink);
      font: inherit;
      text-align: left;
      padding: 0;
      margin: 0;
      cursor: pointer;
      line-height: 1.4;
      flex: 1;
    }

    .word-text:hover {
      text-decoration: underline;
      text-decoration-thickness: 2px;
      text-decoration-color: var(--accent);
    }

    .small {
      font-size: 0.8rem;
      color: #6e5a45;
      min-width: 2.2em;
      text-align: right;
    }

    .meaning {
      grid-column: 1 / -1;
      margin: 6px 0 0;
      padding: 8px 10px;
      border-radius: 8px;
      background: #fbf3e8;
      border: 1px dashed var(--border);
      font-size: 0.92rem;
      line-height: 1.5;
    }

    .meaning[hidden] {
      display: none;
    }

    @keyframes reveal {
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  </style>
</head>
<body>
  <main class="wrap">
    <h1>${SOURCE_LABEL} Pronunciation</h1>
    <p>単語をクリックすると意味を表示します。Play ボタンは発音のみ再生します。</p>
    <div class="controls">
      <button type="button" id="playAll">Play All</button>
      <button type="button" id="stopAll">Stop</button>
    </div>
    <ul class="word-list" id="wordList">
HTML_HEAD

line_no=0
while IFS=$'\t' read -r n word details relpath; do
  line_no=$((line_no + 1))
  delay=$((line_no * 25))
  safe_word=$(printf '%s' "$word" \
    | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' -e 's/"/\&quot;/g')
  safe_details=$(printf '%s' "$details" \
    | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' -e 's/"/\&quot;/g')
  safe_details=${safe_details//\\n/<br>}

  cat >> "$HTML_FILE" <<HTML_ROW
      <li class="word-item" style="animation-delay: ${delay}ms;">
        <button type="button" class="play-btn" data-audio="$relpath" aria-label="Play ${safe_word}">Play</button>
        <button type="button" class="word-text" data-audio="$relpath" aria-expanded="false">${safe_word}</button>
        <span class="small">#${n}</span>
        <p class="meaning" hidden>${safe_details}</p>
      </li>
HTML_ROW
done < "$MAP_FILE"

cat >> "$HTML_FILE" <<'HTML_TAIL'
    </ul>
  </main>

  <script>
    const list = document.getElementById('wordList');
    const playAllButton = document.getElementById('playAll');
    const stopAllButton = document.getElementById('stopAll');

    let currentAudio = null;
    let playQueue = [];
    let queueIndex = 0;

    function stopPlayback() {
      playQueue = [];
      queueIndex = 0;
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
      }
    }

    function playSingle(src) {
      stopPlayback();
      currentAudio = new Audio(src);
      currentAudio.play().catch((err) => {
        console.error('Audio play failed:', err);
      });
    }

    function playQueueNext() {
      if (queueIndex >= playQueue.length) {
        currentAudio = null;
        return;
      }
      const src = playQueue[queueIndex++];
      currentAudio = new Audio(src);
      currentAudio.addEventListener('ended', playQueueNext);
      currentAudio.play().catch((err) => {
        console.error('Audio play failed:', err);
        playQueueNext();
      });
    }

    function closeAllMeanings() {
      document.querySelectorAll('.meaning').forEach((el) => {
        el.hidden = true;
      });
      document.querySelectorAll('.word-text').forEach((el) => {
        el.setAttribute('aria-expanded', 'false');
      });
    }

    list.addEventListener('click', (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;

      if (target.classList.contains('play-btn')) {
        const src = target.getAttribute('data-audio');
        if (src) {
          playSingle(src);
        }
        return;
      }

      if (!target.classList.contains('word-text')) {
        return;
      }

      const item = target.closest('.word-item');
      if (!item) return;

      const meaning = item.querySelector('.meaning');
      if (!(meaning instanceof HTMLElement)) return;

      const willOpen = meaning.hidden;
      closeAllMeanings();
      meaning.hidden = !willOpen;
      target.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
    });

    playAllButton.addEventListener('click', () => {
      stopPlayback();
      closeAllMeanings();
      playQueue = Array.from(document.querySelectorAll('.play-btn[data-audio]'))
        .map((el) => el.getAttribute('data-audio'))
        .filter((src) => !!src);
      queueIndex = 0;
      playQueueNext();
    });

    stopAllButton.addEventListener('click', stopPlayback);
  </script>
</body>
</html>
HTML_TAIL

echo "Generated:"
echo "  Words: $WORDS_FILE"
echo "  Word+Details: $WORD_MEANINGS_FILE"
echo "  Map:   $MAP_FILE"
echo "  Audio: $AUDIO_DIR"
echo "  HTML:  $HTML_FILE"
