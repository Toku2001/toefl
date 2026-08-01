#!/usr/bin/env python3
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "story_learning"
SOURCE_GLOB = "*/知らない単語集*.md"
CHAPTERS = 5

SUMMARY_RE = re.compile(r"<summary>(.*?)</summary>", re.IGNORECASE)
MEANING_RE = re.compile(r"\*\*意味:\*\*\s*(.+)")


def normalize(s: str) -> str:
    return " ".join(s.strip().lower().split())


def parse_entries():
    entries = []
    for path in sorted(ROOT.glob(SOURCE_GLOB)):
        lines = path.read_text(encoding="utf-8").splitlines()
        current = None
        for line in lines:
            sm = SUMMARY_RE.search(line)
            if sm:
                current = sm.group(1).strip()
                continue
            if current:
                mm = MEANING_RE.search(line)
                if mm:
                    entries.append(
                        {
                            "word": current,
                            "meaning": mm.group(1).strip(),
                            "source": str(path.relative_to(ROOT)),
                        }
                    )
                    current = None
    return entries


def build_vocab(entries):
    grouped = defaultdict(list)
    for e in entries:
        grouped[normalize(e["word"])].append(e)

    rows = []
    for key, items in grouped.items():
        word = Counter([i["word"] for i in items]).most_common(1)[0][0]
        meaning = Counter([i["meaning"] for i in items]).most_common(1)[0][0]
        rows.append(
            {
                "key": key,
                "word": word,
                "meaning": meaning,
                "freq": len(items),
            }
        )

    rows.sort(key=lambda x: (-x["freq"], x["key"]))
    for i, r in enumerate(rows, 1):
        r["id"] = i
    return rows


def split_chapters(rows):
    buckets = [[] for _ in range(CHAPTERS)]
    for i, row in enumerate(rows):
        buckets[i % CHAPTERS].append(row)
    return buckets


def chapter_title(i):
    titles = [
        "Episode 1: The Library Under Neon Rain",
        "Episode 2: The Museum of Borrowed Futures",
        "Episode 3: The Train That Runs Through Dreams",
        "Episode 4: The Trial of the Moon Market",
        "Episode 5: The City That Remembers Your Name",
    ]
    return titles[i - 1]


def story_body(i, focus_words):
    tokens = [w["word"] for w in focus_words[:24]]
    while len(tokens) < 24:
        tokens.append("signal")
    keyword_line = ", ".join(tokens)

    plots = {
    1: """Neon rain blurred every sign in Harbor District when Mina received a paper ticket with no sender name. The ticket led her to an underground library where each book contained one erased memory from the city. A curator in a copper coat told her the library had a simple mission: recover true stories before false stories took over public life.

Mina started in Room Seven, where memories were stored as floating glass chips. She watched clips of teachers bargaining for solar batteries, nurses sharing medicine during a blackout, and students painting flood maps on school walls. The city was messy, tired, and brilliant. It had survived not because people agreed all the time, but because they kept meeting, arguing, and trying again.

At midnight, the alarm rang. Someone was replacing verified records with polished fakes. In the central hall, Mina found a trail of silver ink that pointed to the old observatory. There she met a young engineer who confessed he had edited records to hide a budget scandal. "If people see the full report," he said, "they'll lose hope." Mina answered, "Hope built on lies collapses faster than any bridge."

They returned to the library and reopened the original archive. Volunteers arrived from every district, reading, translating, and cross-checking data until dawn. By sunrise, citizens had posted a public timeline that showed both mistakes and repairs. It was imperfect, but it was real.

Before leaving, Mina pinned a training card on the wall: remember, discuss, verify, revise, repeat. The curator laughed and said, "Not glamorous, but powerful." Mina stepped into the rain feeling oddly light. Truth had not solved everything, yet it had given the city a direction. And direction, she realized, was often enough to begin again.

On the final board, she wrote today's key words so new volunteers could study while working. The board read: <<KEYWORDS>>.""",
    2: """The next week, Mina was hired by the Museum of Borrowed Futures, a strange place where broken inventions from the future were displayed with warning labels. The director believed failed prototypes were the best teachers because they showed exactly where confidence had outrun caution.

Exhibit Hall A contained a climate mirror that could cool one neighborhood while overheating another. Hall B held a language headset that translated perfectly but erased regional accents. School groups toured the museum daily, and Mina guided them through each machine's origin story. She asked students not just what a device could do, but who might be excluded, priced out, or silently harmed.

One afternoon, a sponsor demanded that the museum remove "negative narratives" to protect investment. The director hesitated; funding was thin. Mina proposed a compromise: keep the exhibits, add public design labs, and invite sponsors to solve the flaws in open workshops. Surprisingly, the sponsor agreed, partly because cameras were present, partly because students were already cheering.

Within a month, engineers, artists, and local residents built safer versions of old prototypes. The climate mirror gained fairness rules; the language headset kept accent diversity; an autonomous ferry added emergency manual controls. The museum changed from a warning space into a collaboration engine.

At closing time, Mina updated the blackboard near the exit with a rotating study list. "Technology is policy in hardware form," she told the last visitors. "If you can name the risk, you can redesign the system." They copied the list into their notebooks and promised to return next weekend.

Tonight's board words were: <<KEYWORDS>>.""",
    3: """Episode three began on the Dreamline, a midnight train that crossed the city without fixed tracks. Passengers boarded with one question they could not solve alone. The train's walls projected anonymous stories submitted by strangers: family conflicts, startup failures, research dead ends, and private fears that daylight conversations rarely allowed.

Mina volunteered as a "listener conductor." Her job was to pair passengers whose questions could unlock each other. A tired farmer worried about soil decline sat beside a game designer studying motivation loops. A public defender met a biology teacher researching stress and memory. As conversations deepened, improbable connections appeared. Practical advice moved faster than any official program.

At Station Nine, the train lost power in a tunnel. Phones dimmed, displays went black, and panic rose in waves. Mina organized a low-tech session by lantern light: one person shared a challenge, another offered one action they could take within twenty-four hours. No speeches, no saviors, only concrete next steps. By the time emergency crews restored electricity, the carriage felt calmer than before.

The next morning, several passengers created a community channel called Next Step Board. Every post had to include a measurable goal, a partner, and a review date. In three months, the board became a city habit. People still struggled, but fewer struggled alone.

As dawn painted the river silver, Mina wrote the Dreamline's study prompt in large block letters: "Name the pattern, test the pattern, teach the pattern." Commuters photographed it and smiled. Learning, she thought, is just courage repeated in public.

Pinned beneath the prompt was today's keyword chain: <<KEYWORDS>>.""",
    4: """When moon season opened, Harbor District hosted its annual Night Market Trial, a theatrical court where policy ideas were tested before real implementation. Teams performed mini-dramas to defend proposals: flood barriers, transport pricing, school calendars, and food distribution routes. Citizens voted not for charisma, but for evidence quality.

Mina joined Team Lantern, a mixed group of elders, students, coders, cooks, and bus drivers. Their proposal was simple: convert abandoned parking towers into vertical gardens, emergency shelters, and after-school labs. Critics called it unrealistic. Team Lantern responded with maps, maintenance budgets, and a volunteer training schedule. They even brought a prototype irrigation wall built from recycled pipes.

During cross-examination, a rival team claimed the plan would increase inequality. Mina conceded the risk and offered amendments: neighborhood governance quotas, transparent waiting lists, and independent audits every quarter. The crowd murmured approval. Not because the plan was perfect, but because the team showed how to correct failure before failure happened.

After midnight, the judges announced results. Team Lantern won second place, yet their governance amendments won first place in public adoption. In the market square, teenagers started sketching their own versions for different districts. Policy had become a shared craft, not a distant spectacle.

Before closing, Mina climbed the fountain steps and posted a giant revision checklist. "Argument is not war," she told the crowd. "Argument is maintenance for collective thinking." People clapped, laughed, and went back to debating stall by stall.

The checklist ended with today's vocabulary ribbon: <<KEYWORDS>>.""",
    5: """In the final episode, Mina entered the oldest district, where buildings stored personal memories in their walls. Locals called it the City That Remembers Your Name. Doors opened only when spoken to kindly; streetlights brightened when neighbors greeted one another. The entire district ran on social rituals as much as electricity.

But memory walls had begun to fail. Names disappeared overnight, and with them, access to medicine cabinets, legal files, and family letters. Rumors spread that a private firm wanted to replace the district with luxury towers. Mina assembled a repair circle: archivists, electricians, grandparents, and teenagers fluent in legacy code.

They discovered the core issue was not sabotage but neglected maintenance. Updates had been postponed for years because officials assumed old systems would somehow endure forever. Mina's team divided the district into blocks, trained local stewards, and created a public log where every repair action was visible. Trust started returning one porch at a time.

On the final night, residents gathered in the plaza for a naming ceremony. Children read restored family names; elders told migration stories; musicians played songs once thought lost. When Mina stepped to the microphone, she refused to take credit. "Infrastructure is memory," she said, "and memory survives when responsibility is shared."

At midnight, every streetlight turned gold. The walls responded to thousands of voices speaking names together, not perfectly, but with care. Mina looked around and understood the project had never been about nostalgia. It was about designing systems that help people stay visible to one another.

She left one last chalk line on the city gate, a study trail for anyone who wanted to continue: <<KEYWORDS>>.""",
    }

    closing = (
        "\n\nBefore going home, Mina opened her notebook and wrote three review questions for tomorrow: "
        "Which decision was based on evidence? Which conflict became easier after people shared precise language? "
        "Which small routine should be repeated even when no one is watching? She answered each question in two lines, "
        "circled one mistake she wanted to avoid, and chose one action she could complete in less than ten minutes. "
        "That quiet ritual, repeated nightly, made the story practical instead of decorative."
    )
    return plots.get(i, plots[1]).replace("<<KEYWORDS>>", keyword_line) + closing


def write_story(chapter_no, bucket):
    title = chapter_title(chapter_no)
    body = story_body(chapter_no, bucket)
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append("## Story (~400 words)")
    lines.append("")
    lines.append(body)
    lines.append("")
    lines.append("## Vocabulary Used in This Episode")
    lines.append("")
    lines.append("<details>")
    lines.append(f"<summary>Open vocabulary list ({len(bucket)} items)</summary>")
    lines.append("")
    for row in bucket:
        lines.append(f"- {row['word']} : {row['meaning']}")
    lines.append("")
    lines.append("</details>")
    lines.append("")
    (OUT / f"story_{chapter_no:02d}.md").write_text("\n".join(lines), encoding="utf-8")


def write_coverage(buckets):
    lines = ["id\tchapter\tword\tmeaning\tfrequency"]
    for i, bucket in enumerate(buckets, 1):
        for row in bucket:
            lines.append(f"{row['id']}\t{i}\t{row['word']}\t{row['meaning']}\t{row['freq']}")
    (OUT / "vocabulary_coverage.tsv").write_text("\n".join(lines), encoding="utf-8")


def write_readme(total, entries, buckets):
    lines = []
    lines.append("# 5-Story Vocabulary Learning Pack")
    lines.append("")
    lines.append("3か月分の『知らない単語集』を、5本の連続ストーリー教材に再構成したセットです。")
    lines.append("")
    lines.append(f"- 元エントリ数: {entries}")
    lines.append(f"- ユニーク語彙数: {total}")
    lines.append(f"- 章数: {len(buckets)}")
    lines.append("")
    lines.append("## Files")
    lines.append("- story_01.md - story_05.md: 各章の本文（約400語）+ その章の語彙")
    lines.append("- vocabulary_coverage.tsv: 1384語の章割り当て一覧")
    lines.append("")
    lines.append("## Regenerate")
    lines.append("```bash")
    lines.append("cd /Users/tokuhisa/git/toefl")
    lines.append("python3 SantaAI/単語集/build_story_learning.py")
    lines.append("```")
    lines.append("")
    lines.append("## Daily Use (15-20 min)")
    lines.append("1. 1日1章を音読（意味を見ない）")
    lines.append("2. 同章の語彙リストを開いて答え合わせ")
    lines.append("3. 難しかった語だけノートに10語メモ")
    lines.append("4. 翌日は次の章へ進み、6日目に第1章へ戻る")
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = parse_entries()
    vocab = build_vocab(entries)
    buckets = split_chapters(vocab)

    for i, bucket in enumerate(buckets, 1):
        write_story(i, bucket)

    write_coverage(buckets)
    write_readme(total=len(vocab), entries=len(entries), buckets=buckets)

    print(f"Generated at: {OUT}")
    print(f"entries={len(entries)}, unique={len(vocab)}, chapters={len(buckets)}")
    print("chapter sizes:", ", ".join(str(len(b)) for b in buckets))


if __name__ == "__main__":
    main()
