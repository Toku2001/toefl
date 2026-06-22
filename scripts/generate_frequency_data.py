#!/usr/bin/env python3

"""Generate frequency rankings for recurring TOEFL vocabulary.

The script scans source markdown files that contain <details>/<summary> word
entries, counts repeated headwords across the repository, and writes a JSON and
TSV summary that can be consumed by a future quiz page.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "data"
JSON_PATH = OUTPUT_DIR / "word_frequency.json"
TSV_PATH = OUTPUT_DIR / "word_frequency.tsv"


@dataclass(frozen=True)
class Entry:
    word: str
    normalized_word: str
    source_file: str
    subject: str
    entry_index: int
    meaning: str = ""
    basic_form: str = ""
    accent: str = ""
    synonyms: str = ""
    details: str = ""


def iter_source_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        parts = relative.parts

        if relative.name in {"README.md", "makeGithubPages.md", "makeGrammar.md", "makePronunciation.md", "makewordlist.md", "makeserver.md"}:
            continue
        if parts[0] == ".git" or parts[0] == ".vscode":
            continue
        if any(part.startswith("_") for part in parts):
            continue
        if any(part.endswith("_pronunciation") for part in parts):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if "<summary>" not in content or "<details>" not in content:
            continue

        yield path


def normalize_word(word: str) -> str:
    text = word.casefold().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^[\s\"'“”‘’\(\)\[\]{}.,!?;:]+", "", text)
    text = re.sub(r"[\s\"'“”‘’\(\)\[\]{}.,!?;:]+$", "", text)
    return text


def extract_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip().replace("**", "")
        match = re.match(r"^(.+?):\s*(.*)$", line)
        if not match:
            continue

        label = match.group(1).strip()
        value = match.group(2).strip()
        if label in {"意味", "基本形", "アクセント", "類義語"}:
            fields[label] = value

    return fields


def preview_path_from_source(source_file: str) -> str:
    if source_file == "Law/18words.md":
        candidate = "Law/pronunciation/index.html"
        return candidate if (REPO_ROOT / candidate).exists() else source_file

    path = Path(source_file)
    candidate = path.parent / f"{path.stem}_pronunciation" / "index.html"
    return str(candidate) if (REPO_ROOT / candidate).exists() else source_file


def audio_path_from_entry(word: str, source_file: str) -> str:
    """Find the audio file for a given word in its pronunciation directory."""
    audio_dir = Path(source_file).parent / f"{Path(source_file).stem}_pronunciation" / "audio"
    if not (REPO_ROOT / audio_dir).exists():
        return ""

    slug = (
        word.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace("'", "")
    )
    slug = re.sub(r"[^a-z0-9_-]", "", slug)
    slug = re.sub(r"_+", "_", slug).strip("_")

    # Try to find matching audio file with pattern like 001_*.mp3, 002_*.mp3, etc.
    audio_root = REPO_ROOT / audio_dir
    if not audio_root.exists():
        return ""

    for audio_file in audio_root.glob("*.mp3"):
        # Match by filename containing the slug
        if slug and slug in audio_file.stem.lower():
            return str(audio_dir / audio_file.name)

    return ""


def parse_word_entries(path: Path) -> list[Entry]:
    entries: list[Entry] = []
    in_details = False
    current_word = ""
    entry_index = 0
    detail_lines: list[str] = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return entries

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("<details>"):
            in_details = True
            current_word = ""
            detail_lines = []
            continue

        if stripped.startswith("</details>"):
            if current_word:
                fields = extract_fields(detail_lines)
                entry_index += 1
                entries.append(
                    Entry(
                        word=current_word,
                        normalized_word=normalize_word(current_word),
                        source_file=str(path.relative_to(REPO_ROOT)),
                        subject=str(path.relative_to(REPO_ROOT).parts[0]),
                        entry_index=entry_index,
                        meaning=fields.get("意味", ""),
                        basic_form=fields.get("基本形", ""),
                        accent=fields.get("アクセント", ""),
                        synonyms=fields.get("類義語", ""),
                        details="\n".join(detail_lines),
                    )
                )
            in_details = False
            current_word = ""
            detail_lines = []
            continue

        if in_details and "<summary>" in stripped:
            current_word = re.sub(r"^.*<summary>", "", stripped)
            current_word = re.sub(r"</summary>.*$", "", current_word).strip()
            continue

        if in_details and current_word:
            if stripped:
                detail_lines.append(stripped)
            continue

    return entries


def build_rankings(entries: list[Entry]) -> list[dict[str, object]]:
    grouped: dict[str, list[Entry]] = defaultdict(list)
    for entry in entries:
        grouped[entry.normalized_word].append(entry)

    ranked: list[dict[str, object]] = []
    counts = Counter(entry.normalized_word for entry in entries)

    for rank, (normalized_word, group) in enumerate(
        sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])),
        start=1,
    ):
        first = min(group, key=lambda entry: (entry.source_file, entry.entry_index))
        ranked.append(
            {
                "rank": rank,
                "word": first.word,
                "normalized_word": normalized_word,
                "count": counts[normalized_word],
                "subjects": sorted({entry.subject for entry in group}),
                "files": sorted({entry.source_file for entry in group}),
                "first_seen": first.source_file,
                "preview_path": preview_path_from_source(first.source_file),
                "audio_path": audio_path_from_entry(first.word, first.source_file),
                "meaning": first.meaning,
                "basic_form": first.basic_form,
                "accent": first.accent,
                "synonyms": first.synonyms,
                "occurrences": [asdict(entry) for entry in group],
            }
        )

    return ranked


def cleanup_audio_files(rankings: list[dict]) -> tuple[int, list[dict]]:
    """Keep only audio files for top 100 words, remove others.
    
    Args:
        rankings: List of ranked word dictionaries.
    
    Returns:
        Tuple of (number of audio files removed, list of top 100 words without audio)
    """
    top_100 = rankings[:100]
    
    # Collect audio paths for top 100 words
    kept_audio_paths = set()
    missing_audio = []
    
    for item in top_100:
        if item.get("audio_path"):
            kept_audio_paths.add(str(REPO_ROOT / item["audio_path"]))
        else:
            missing_audio.append(item)
    
    # Find and remove audio files not in top 100
    removed_count = 0
    for audio_file in REPO_ROOT.rglob("*/audio/*.mp3"):
        if str(audio_file) not in kept_audio_paths:
            audio_file.unlink()
            removed_count += 1
    
    return removed_count, missing_audio


def generate_missing_audio(missing_audio: list[dict]) -> tuple[int, list[str]]:
    """Generate audio files for missing words using gTTS or local TTS.
    
    Args:
        missing_audio: List of word dictionaries without audio.
    
    Returns:
        Tuple of (number of generated files, list of error messages)
    """
    if not missing_audio:
        return 0, []
    
    if not HAS_GTTS and not HAS_PYTTSX3:
        return 0, ["Neither gTTS nor pyttsx3 installed. Run: pip install gtts"]
    
    generated_count = 0
    errors = []
    
    # Try gTTS first (cloud-based, more reliable)
    use_gtts = HAS_GTTS
    
    if not use_gtts and HAS_PYTTSX3:
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
        except Exception as e:
            errors.append(f"Failed to initialize pyttsx3: {e}")
            return 0, errors
    
    for item in missing_audio:
        word = item["word"]
        subject = item["subjects"][0] if item["subjects"] else "SantaAI"
        
        # Find or create pronunciation directory
        subject_path = REPO_ROOT / subject
        if not subject_path.exists():
            errors.append(f"Subject directory not found: {subject} (word: {word})")
            continue
        
        # Look for existing pronunciation directory pattern
        audio_dir = None
        for pron_dir in subject_path.glob("*_pronunciation"):
            audio_dir = pron_dir / "audio"
            break
        
        # If no pronunciation directory exists, create a new one
        if audio_dir is None:
            pron_dir = subject_path / f"{subject}_pronunciation"
            audio_dir = pron_dir / "audio"
        
        # Create audio directory if needed
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        slug = (
            word.lower()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .replace("'", "")
        )
        slug = re.sub(r"[^a-z0-9_-]", "", slug)
        slug = re.sub(r"_+", "_", slug).strip("_")
        
        filename = f"{item['rank']:03d}_{slug}.mp3"
        filepath = audio_dir / filename
        
        try:
            if use_gtts:
                # Use gTTS (Google Text-to-Speech)
                tts = gTTS(text=word, lang='en', slow=False)
                tts.save(str(filepath))
            else:
                # Use local pyttsx3
                engine.save_to_file(word, str(filepath))
                engine.runAndWait()
            
            generated_count += 1
        except Exception as e:
            errors.append(f"Failed to generate audio for '{word}': {e}")
    
    return generated_count, errors


def main() -> int:
    entries: list[Entry] = []
    source_files = list(iter_source_files(REPO_ROOT))

    for path in source_files:
        entries.extend(parse_word_entries(path))

    rankings = build_rankings(entries)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "source_file_count": len(source_files),
        "entry_count": len(entries),
        "unique_word_count": len(rankings),
        "items": rankings,
    }

    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with TSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["rank", "word", "normalized_word", "count", "subjects", "files", "first_seen", "preview_path", "audio_path", "meaning", "basic_form", "accent", "synonyms"])
        for item in rankings:
            writer.writerow(
                [
                    item["rank"],
                    item["word"],
                    item["normalized_word"],
                    item["count"],
                    ",".join(item["subjects"]),
                    ",".join(item["files"]),
                    item["first_seen"],
                    item["preview_path"],
                    item["audio_path"],
                    item["meaning"],
                    item["basic_form"],
                    item["accent"],
                    item["synonyms"],
                ]
            )

    # Clean up audio files: keep only top 100
    removed_count, missing_audio = cleanup_audio_files(rankings)
    
    # Try to generate missing audio files
    generated_count, generation_errors = generate_missing_audio(missing_audio)
    
    # Update missing_audio list after generation attempt
    # (Re-detect audio files after generation)
    for item in missing_audio[:]:
        audio_path = audio_path_from_entry(item["word"], item["first_seen"])
        if audio_path:
            missing_audio.remove(item)
            item["audio_path"] = audio_path

    print(f"Wrote {JSON_PATH.relative_to(REPO_ROOT)}")
    print(f"Wrote {TSV_PATH.relative_to(REPO_ROOT)}")
    print(f"Entries: {len(entries)}")
    print(f"Unique words: {len(rankings)}")
    print(f"\n=== Audio File Management ===")
    print(f"Top 100 words: {len(rankings[:100])}")
    print(f"Audio files kept: {len(rankings[:100]) - len(missing_audio)}")
    print(f"Audio files removed: {removed_count}")
    print(f"Audio files generated: {generated_count}")
    
    if generated_count > 0:
        print(f"\n✅ Generated {generated_count} audio files using TTS")
    
    if generation_errors:
        print(f"\n⚠️  Generation errors:")
        for error in generation_errors:
            print(f"  - {error}")
    
    if missing_audio:
        print(f"\n⚠️  Still missing audio files for {len(missing_audio)} words in top 100:")
        print(f"Coverage: {100 * (len(rankings[:100]) - len(missing_audio)) // len(rankings[:100])}%\n")
        for item in missing_audio:
            subject = item["first_seen"].split("/")[0]
            base_name = item["word"].lower().replace(" ", "_").replace("'", "")
            print(f"  {item['rank']:3d}. {item['word']:30s}")
        
        if not HAS_GTTS and not HAS_PYTTSX3:
            print(f"\n💡 To auto-generate missing audio, install gTTS:")
            print(f"   python3 -m pip install gtts")
            print(f"   python3 scripts/generate_frequency_data.py")
        elif not HAS_GTTS:
            print(f"\n💡 For better reliability, install gTTS:")
            print(f"   python3 -m pip install gtts")
            print(f"   python3 scripts/generate_frequency_data.py")
        else:
            print(f"\nTo auto-generate remaining files, re-run this script.")
    else:
        print(f"\n✅ All top 100 words have audio files!")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())