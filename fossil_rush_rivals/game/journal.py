from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import json

from .fossils import Fossil, SET_PIECES

FOSSIL_FACTS = {
    "fossil_ammonite": {
        "description": "Spiral-shelled cephalopod fossil common in marine rock beds.",
        "facts": "Ammonites vanished with the dinosaurs but left abundant shells.",
        "year_discovered": "1799",
        "restoration_notes": "Shell ridges respond well to gentle abrasion cleaning.",
        "showcase_notes": "Spiral silhouette reads clearly under strong museum light.",
    },
    "fossil_trilobite": {
        "description": "Segmented marine arthropod known for its armored exoskeleton.",
        "facts": "Trilobites dominated Paleozoic seas for over 250 million years.",
        "year_discovered": "1698",
        "restoration_notes": "Segment lines are fragile and chip if rushed.",
        "showcase_notes": "Segment symmetry makes it a crowd favorite.",
    },
    "fossil_shark_tooth": {
        "description": "Compact tooth fossil with serrated edges and dense enamel.",
        "facts": "Shark teeth are among the most common fossil finds worldwide.",
        "year_discovered": "1667",
        "restoration_notes": "Polish enhances enamel sheen without weakening the tooth.",
        "showcase_notes": "Edge detail pops with high contrast lighting.",
    },
    "fossil_fern": {
        "description": "Plant impression fossil preserving delicate leaf patterns.",
        "facts": "Fern fossils often appear as carbon films in shale.",
        "year_discovered": "1820",
        "restoration_notes": "Moisture control prevents leaf impressions from flaking.",
        "showcase_notes": "Impression casts read well in angled light.",
    },
    "fossil_wood": {
        "description": "Mineralized wood with preserved growth rings and texture.",
        "facts": "Petrified wood forms when minerals replace organic tissue.",
        "year_discovered": "1737",
        "restoration_notes": "Ring patterns sharpen after light surface brushing.",
        "showcase_notes": "Cross sections highlight ring density.",
    },
    "fossil_brachiopod": {
        "description": "Marine shell fossil with bilateral symmetry.",
        "facts": "Brachiopods resemble clams but have different internal anatomy.",
        "year_discovered": "1742",
        "restoration_notes": "Shell hinges are brittle and need careful handling.",
        "showcase_notes": "Symmetry reads best in shallow shadow.",
    },
    "fossil_crinoid": {
        "description": "Stacked stem segments from a sea lily-like animal.",
        "facts": "Crinoids are echinoderms related to sea stars.",
        "year_discovered": "1735",
        "restoration_notes": "Stem segments align cleanly after a gentle wash.",
        "showcase_notes": "Columnar structure is great for scale displays.",
    },
    "fossil_coprolite": {
        "description": "Fossilized waste with preserved inclusions.",
        "facts": "Coprolites reveal diet details of extinct animals.",
        "year_discovered": "1829",
        "restoration_notes": "Surface cracks need stabilization before display.",
        "showcase_notes": "Labeling helps audiences understand its role.",
    },
    "fossil_bone_fragment": {
        "description": "Small fossil bone shard with rough cortical texture.",
        "facts": "Fragments can identify larger animals through microstructure.",
        "year_discovered": "1850",
        "restoration_notes": "Consolidant improves durability without altering shape.",
        "showcase_notes": "Pair with comparative samples for clarity.",
    },
    "set_triceratops_torso": {
        "description": "Torso fragment from a Triceratops display set.",
        "facts": "Triceratops had sturdy rib cages to support their bulk.",
        "year_discovered": "1888",
        "restoration_notes": "Rib impressions need gentle cleaning to stay crisp.",
        "showcase_notes": "Pairs well with skull details for a full silhouette.",
    },
    "set_triceratops_skull": {
        "description": "Skull fragment with broad bony plates.",
        "facts": "Triceratops skulls could be over two meters long.",
        "year_discovered": "1889",
        "restoration_notes": "Plate edges are fragile and need support.",
        "showcase_notes": "Skull contours read well in profile lighting.",
    },
    "set_triceratops_tail": {
        "description": "Tail fragment from a Triceratops display set.",
        "facts": "Tail vertebrae helped balance the heavy skull.",
        "year_discovered": "1890",
        "restoration_notes": "Segment edges chip under heavy brushing.",
        "showcase_notes": "Showcase with torso pieces for scale.",
    },
    "set_mosasaur_tooth": {
        "description": "Large tooth fragment from a marine predator.",
        "facts": "Mosasaur teeth show heavy wear from hunting.",
        "year_discovered": "1764",
        "restoration_notes": "Keep serrations intact to preserve detail.",
        "showcase_notes": "Contrasting backdrop highlights tooth shape.",
    },
    "set_mosasaur_torso": {
        "description": "Torso fragment from a marine predator set.",
        "facts": "Mosasaur torsos were built for powerful swimming.",
        "year_discovered": "1770",
        "restoration_notes": "Rings are stable but need crack monitoring.",
        "showcase_notes": "Displays well with scale markers.",
    },
    "set_mosasaur_skull": {
        "description": "Skull fragment from a mosasaur set.",
        "facts": "Mosasaur skulls had long jaws lined with teeth.",
        "year_discovered": "1784",
        "restoration_notes": "Jaw edges need support to prevent fractures.",
        "showcase_notes": "Pair with tooth fragments for impact.",
    },
    "set_mammoth_skull": {
        "description": "Skull fragment from an ice age mammoth.",
        "facts": "Mammoth skulls anchored massive tusks and neck muscles.",
        "year_discovered": "1799",
        "restoration_notes": "Avoid heavy polishing to preserve surface texture.",
        "showcase_notes": "Pairs well with torso fragments for scale.",
    },
    "set_mammoth_torso": {
        "description": "Torso fragment from a mammoth set piece.",
        "facts": "Mammoth torsos were supported by dense rib bones.",
        "year_discovered": "1801",
        "restoration_notes": "Surface consolidation improves structural integrity.",
        "showcase_notes": "Scale comparisons help emphasize size.",
    },
    "set_trex_skull": {
        "description": "Large skull fragment from a Tyrannosaurus Rex.",
        "facts": "T-Rex skulls had a powerful bite force.",
        "year_discovered": "1902",
        "restoration_notes": "Fragile bone structures require careful stabilization.",
        "showcase_notes": "Displays best with jaws open for maximum effect.",
    },
    "set_trex_torso": {
        "description": "Vertebra fragment from a Tyrannosaurus Rex.",
        "facts": "T-Rex spines were robust to support massive weight.",
        "year_discovered": "1905",
        "restoration_notes": "Keep vertebrae aligned properly.",
        "showcase_notes": "Great for demonstrating sheer scale.",
    },
    "set_trex_feet": {
        "description": "Foot bone fragment from a Tyrannosaurus Rex.",
        "facts": "T-Rex feet had three large forward-facing toes.",
        "year_discovered": "1902",
        "restoration_notes": "Claw tips are fragile.",
        "showcase_notes": "Place near base to emphasize ground impact.",
    },
}


def _journal_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "data" / "journal.json"


def _default_journal() -> Dict[str, object]:
    return {
        "entries": {},
        "sets": {},
        "best_auction": 0,
        "market_trends": {},
        "last_updated": "",
    }


def load_journal() -> Dict[str, object]:
    path = _journal_path()
    if not path.exists():
        return _default_journal()
    return json.loads(path.read_text())


def save_journal(journal: Dict[str, object]) -> None:
    path = _journal_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(journal, indent=2))


def _set_display_name(set_id: str) -> str:
    pieces = SET_PIECES.get(set_id, [])
    if not pieces:
        return set_id.replace("_", " ").title()
    if set_id == "triceratops_display":
        return "Triceratops Display Set"
    if set_id == "marine_predator":
        return "Marine Predator Set"
    if set_id == "ice_age_mammoth":
        return "Ice Age Mammoth Set"
    if set_id == "apex_predator":
        return "Apex Predator Set"
    return set_id.replace("_", " ").title()


def _fossil_display_name(fossil_id: str) -> str:
    for pieces in SET_PIECES.values():
        for piece_id, name in pieces:
            if piece_id == fossil_id:
                return name
    return fossil_id.replace("_", " ").title()


def _set_piece_counts(entries: Dict[str, dict], set_id: str) -> tuple[int, int]:
    pieces = SET_PIECES.get(set_id, [])
    total = len(pieces)
    found = 0
    for fossil_id, _name in pieces:
        entry = entries.get(fossil_id)
        if entry and int(entry.get("discovered", 0)) > 0:
            found += 1
    return found, total


def update_from_match(
    journal: Dict[str, object],
    fossils: Dict[str, Fossil],
    player_score: int,
    market_trend: str,
) -> Dict[str, object]:
    updated = dict(journal)
    entries: Dict[str, dict] = dict(updated.get("entries", {}))
    sets: Dict[str, dict] = dict(updated.get("sets", {}))
    trends: Dict[str, int] = dict(updated.get("market_trends", {}))

    today = date.today().isoformat()

    for fossil in fossils.values():
        if fossil.owner != "player":
            continue
        entry = entries.get(fossil.fossil_id, {})
        entry["name"] = fossil.name
        facts = FOSSIL_FACTS.get(fossil.fossil_id, {})
        entry["description"] = facts.get("description", "")
        entry["discovered"] = int(entry.get("discovered", 0)) + 1
        entry["last_found"] = today
        if fossil.verified or fossil.lab_focus_applied == "Authenticate":
            year_discovered = str(facts.get("year_discovered", ""))
            if year_discovered:
                entry["year_discovered"] = year_discovered
            entry["facts"] = facts.get("facts", entry.get("facts", ""))
            entry["authenticated"] = True
        if fossil.lab_focus_applied == "Restore":
            entry["restoration_notes"] = facts.get("restoration_notes", entry.get("restoration_notes", ""))
        if fossil.lab_focus_applied == "Showcase Prep":
            entry["showcase_notes"] = facts.get("showcase_notes", entry.get("showcase_notes", ""))
        entries[fossil.fossil_id] = entry

    for set_id in SET_PIECES:
        pieces = SET_PIECES[set_id]
        completed = True
        for fossil_id, _name in pieces:
            fossil = fossils.get(fossil_id)
            if not fossil or fossil.owner != "player" or fossil.broken:
                completed = False
                break
        if not completed:
            continue
        record = sets.get(set_id, {})
        record["name"] = _set_display_name(set_id)
        record["completed"] = int(record.get("completed", 0)) + 1
        record["last_completed"] = today
        sets[set_id] = record

    best_auction = int(updated.get("best_auction", 0))
    updated["best_auction"] = max(best_auction, player_score)
    if market_trend:
        trends[market_trend] = int(trends.get(market_trend, 0)) + 1

    updated["entries"] = entries
    updated["sets"] = sets
    updated["market_trends"] = trends
    updated["last_updated"] = today
    return updated


def build_journal_view(
    journal: Dict[str, object],
    view: str,
    show_sets: bool,
    show_individuals: bool,
) -> tuple[List[Dict[str, str]], str]:
    cards: List[Dict[str, str]] = []
    entries: Dict[str, dict] = journal.get("entries", {})  # type: ignore[assignment]
    sets: Dict[str, dict] = journal.get("sets", {})  # type: ignore[assignment]

    if view.startswith("set:"):
        set_id = view.split(":", 1)[1]
        for fossil_id, name in SET_PIECES.get(set_id, []):
            entry = entries.get(fossil_id, {})
            count = int(entry.get("discovered", 0))
            subtitle = f"Found {count}x" if count > 0 else "Missing"
            cards.append(
                {
                    "key": f"fossil:{fossil_id}",
                    "title": name,
                    "subtitle": subtitle,
                }
            )
        title = f"{_set_display_name(set_id)} Pieces"
        return cards, title

    if show_sets:
        for set_id in SET_PIECES:
            found, total = _set_piece_counts(entries, set_id)
            if found == 0:
                continue
            name = str(sets.get(set_id, {}).get("name", _set_display_name(set_id)))
            cards.append(
                {
                    "key": f"set:{set_id}",
                    "title": name,
                    "subtitle": f"{found}/{total} pieces",
                }
            )

    if show_individuals:
        for fossil_id, entry in entries.items():
            name = str(entry.get("name", fossil_id))
            count = int(entry.get("discovered", 0))
            cards.append(
                {
                    "key": f"fossil:{fossil_id}",
                    "title": name,
                    "subtitle": f"Found {count}x",
                }
            )

    cards.sort(key=lambda item: item["title"].lower())
    return cards, "Field Journal"


def get_entry_details(journal: Dict[str, object], key: Optional[str]) -> Optional[Dict[str, object]]:
    if not key:
        return None
    entries: Dict[str, dict] = journal.get("entries", {})  # type: ignore[assignment]
    sets: Dict[str, dict] = journal.get("sets", {})  # type: ignore[assignment]

    if key.startswith("fossil:"):
        fossil_id = key.split(":", 1)[1]
        entry = entries.get(fossil_id, {})
        name = str(entry.get("name", _fossil_display_name(fossil_id)))
        discovered = int(entry.get("discovered", 0))
        last_found = str(entry.get("last_found", ""))
        title = name
        subtitle = f"Discovered: {discovered}"
        detail = f"Last found: {last_found}" if last_found else ""
        description = str(entry.get("description", ""))
        lines: List[str] = []
        if description:
            lines.append(description)
        facts = str(entry.get("facts", ""))
        if facts:
            lines.append(facts)
        year_discovered = str(entry.get("year_discovered", ""))
        if year_discovered:
            lines.append(f"Year discovered: {year_discovered}")
        restoration_notes = str(entry.get("restoration_notes", ""))
        if restoration_notes:
            lines.append(restoration_notes)
        showcase_notes = str(entry.get("showcase_notes", ""))
        if showcase_notes:
            lines.append(showcase_notes)
        if not lines:
            lines.append("Lab work reveals more information over time.")
        return {
            "title": title,
            "subtitle": subtitle,
            "detail": detail,
            "lines": lines,
            "found_count": discovered,
        }

    if key.startswith("set:"):
        set_id = key.split(":", 1)[1]
        record = sets.get(set_id)
        if not record:
            return None
        name = str(record.get("name", _set_display_name(set_id)))
        completed = int(record.get("completed", 0))
        last_completed = str(record.get("last_completed", ""))
        subtitle = f"Completed: {completed}"
        detail = f"Last completed: {last_completed}" if last_completed else ""
        return {
            "title": name,
            "subtitle": subtitle,
            "detail": detail,
            "lines": [],
        }

    return None
