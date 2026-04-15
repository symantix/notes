#!/usr/bin/env python3
import argparse
import os
import re
import json
import unicodedata
from datetime import datetime
from pathlib import Path


BAD_TITLE_PATTERN = re.compile(
    r"^(untitled|new note|note|document|text|draft|scratch)(\s*\d+)?$",
    re.IGNORECASE,
)
DATE_TITLE_PATTERN = re.compile(
    r"^(?:\d{4}[-_/]\d{1,2}[-_/]\d{1,2}|\d{1,2}[-_/]\d{1,2}[-_/]\d{2,4}|\d{8})$"
)
TIME_TITLE_PATTERN = re.compile(
    r"^(?:\d{6}|\d{1,2}[-_:]\d{2}(?:[-_:]\d{2})?)(?:\s?[APap][Mm])?$"
)

SKIP_DIRS = {".obsidian", ".smart-env", ".git", "scripts"}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "if",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "with",
    "you",
    "your",
}


def is_meaningful_title(stem: str) -> bool:
    cleaned = stem.strip()
    if not cleaned:
        return False
    if len(cleaned) < 4:
        return False
    if BAD_TITLE_PATTERN.fullmatch(cleaned):
        return False
    if DATE_TITLE_PATTERN.fullmatch(cleaned):
        return False
    if TIME_TITLE_PATTERN.fullmatch(cleaned):
        return False
    return True


def first_sentence(text: str) -> str:
    compact = " ".join(text.split())
    if not compact:
        return ""
    parts = re.split(r"[.!?]", compact, maxsplit=1)
    candidate = parts[0].strip()
    if len(candidate) < 4:
        words = compact.split()
        return " ".join(words[:8]).strip()
    return candidate


def extract_title_from_content(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        if stripped:
            if len(stripped) < 4:
                return first_sentence(text)
            return stripped
    return ""


def short_title_from_text(text: str) -> str:
    base = extract_title_from_content(text)
    if not base:
        base = first_sentence(text)
    if not base:
        return ""
    base = re.sub(r"[\"'`]+", "", base)
    words = [w for w in re.split(r"\s+", base) if w]
    if len(words) <= 8:
        return " ".join(words)
    content_words = [w for w in words if w.lower() not in STOPWORDS]
    if len(content_words) >= 4:
        words = content_words
    return " ".join(words[:8])


def sanitize_filename(title: str, extension: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[\\/:*?\"<>|]", "", ascii_only)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    if not cleaned:
        cleaned = "Untitled Note"
    if len(cleaned) > 60:
        cleaned = cleaned[:60].rstrip()
    return f"{cleaned}{extension}"


def ensure_unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    extension = path.suffix
    counter = 1
    while True:
        candidate = path.with_name(f"{stem} ({counter}){extension}")
        if not candidate.exists():
            return candidate
        counter += 1


def file_hash(path: Path) -> str:
    try:
        import hashlib

        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return ""


def resolve_target_with_dup(
    source: Path, desired_name: str, extension: str
) -> tuple[Path, bool]:
    desired = source.with_name(f"{desired_name}{extension}")
    if not desired.exists():
        return desired, False
    if file_hash(source) and file_hash(source) == file_hash(desired):
        return desired, True
    return ensure_unique_path(desired), False


def iter_note_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for filename in filenames:
            if filename.startswith("."):
                continue
            ext = Path(filename).suffix.lower()
            if ext not in {".md", ".txt"}:
                continue
            yield Path(dirpath) / filename


def list_candidates(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in iter_note_files(root):
        if not is_meaningful_title(path.stem):
            candidates.append(path)
    return sorted(candidates)


def extract_plan_from_text(text: str) -> dict:
    start = text.find("BEGIN_JSON")
    end = text.find("END_JSON")
    if start == -1 or end == -1 or end <= start:
        return {}
    json_block = text[start + len("BEGIN_JSON"):end].strip()
    if not json_block:
        return {}
    if json_block.startswith("```"):
        json_block = re.sub(r"^```[a-zA-Z0-9]*\n", "", json_block)
        json_block = re.sub(r"\n```$", "", json_block)
    try:
        return json.loads(json_block)
    except json.JSONDecodeError:
        return {}


def apply_plan(plan: dict, root: Path, log_path: Path) -> None:
    log_lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_lines.append(f"[{timestamp}] Applying Cursor CLI plan")

    deletions = plan.get("deletions", []) or []
    renames = plan.get("renames", []) or []

    deleted_count = 0
    for item in deletions:
        rel_path = Path(item.get("path", "")).as_posix()
        if not rel_path:
            continue
        target = root / rel_path
        if not target.exists():
            continue
        try:
            target.unlink()
            log_lines.append(f"Deleted empty file: {target}")
            deleted_count += 1
        except OSError:
            continue

    renamed_count = 0
    for item in renames:
        rel_from = Path(item.get("from", "")).as_posix()
        rel_to = item.get("to", "")
        if not rel_from or not rel_to:
            continue
        source = root / rel_from
        if not source.exists():
            continue
        extension = source.suffix
        to_name = Path(rel_to).name
        if not to_name:
            continue
        if not to_name.lower().endswith(extension.lower()):
            to_name = f"{to_name}{extension}"
        sanitized = sanitize_filename(Path(to_name).stem, extension)
        target, is_duplicate = resolve_target_with_dup(source, Path(sanitized).stem, extension)
        try:
            if is_duplicate:
                source.unlink()
                log_lines.append(f"Deleted duplicate original: {source}")
            else:
                os.rename(source, target)
                log_lines.append(f"Renamed: {source} -> {target}")
                renamed_count += 1
                if source.exists():
                    if file_hash(source) == file_hash(target):
                        try:
                            source.unlink()
                            log_lines.append(f"Deleted duplicate original: {source}")
                        except OSError:
                            pass
        except OSError:
            continue

    end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_lines.append(
        f"[{end_timestamp}] Plan applied. Renamed {renamed_count} file(s). "
        f"Deleted {deleted_count} empty file(s)."
    )
    log_lines.extend(["", ""])
    append_log(log_path, log_lines)


def append_log(log_path: Path, lines: list[str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{line}\n")


def rename_notes(root: Path, dry_run: bool, log_path: Path) -> int:
    log_lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not dry_run:
        log_lines.append(f"[{timestamp}] Run started (dry_run={dry_run})")
    renamed_count = 0
    deleted_count = 0
    for path in iter_note_files(root):
        stem = path.stem
        if is_meaningful_title(stem):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not content.strip():
            if dry_run:
                print(f"DRY RUN: delete empty file {path}")
            else:
                try:
                    path.unlink()
                    print(f"Deleted empty file: {path}")
                    log_lines.append(f"Deleted empty file: {path}")
                    deleted_count += 1
                except OSError:
                    pass
            continue
        title = short_title_from_text(content)
        if not title:
            continue
        new_name = sanitize_filename(title, path.suffix)
        if new_name.lower() == path.name.lower():
            continue
        target, is_duplicate = resolve_target_with_dup(path, Path(new_name).stem, path.suffix)
        if dry_run:
            print(f"DRY RUN: {path} -> {target}")
        else:
            if is_duplicate:
                path.unlink()
                print(f"Deleted duplicate original: {path}")
                log_lines.append(f"Deleted duplicate original: {path}")
            else:
                os.rename(path, target)
                print(f"Renamed: {path} -> {target}")
                log_lines.append(f"Renamed: {path} -> {target}")
                if path.exists():
                    if file_hash(path) == file_hash(target):
                        try:
                            path.unlink()
                            log_lines.append(f"Deleted duplicate original: {path}")
                        except OSError:
                            pass
                renamed_count += 1
    if not dry_run:
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_lines.append(
            f"[{end_timestamp}] Run finished. Renamed {renamed_count} file(s). "
            f"Deleted {deleted_count} empty file(s)."
        )
        log_lines.extend(["", ""])
        append_log(log_path, log_lines)
    return renamed_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rename untitled .md/.txt files based on content."
    )
    parser.add_argument(
        "--root",
        default=str(Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Notes"),
        help="Root Notes directory to scan.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only.")
    parser.add_argument(
        "--list-candidates",
        action="store_true",
        help="Print files with non-meaningful titles and exit.",
    )
    parser.add_argument(
        "--apply-plan-file",
        help="Apply a Cursor CLI JSON plan output file.",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser()
    if not root.exists():
        raise SystemExit(f"Root path does not exist: {root}")

    if args.list_candidates:
        for path in list_candidates(root):
            print(path.relative_to(root))
        return

    if args.apply_plan_file:
        plan_text = Path(args.apply_plan_file).read_text(encoding="utf-8", errors="ignore")
        plan = extract_plan_from_text(plan_text)
        if not plan:
            raise SystemExit("No valid JSON plan found.")
        log_path = root / "scripts" / "rename_notes.log"
        apply_plan(plan, root, log_path)
        return

    log_path = root / "scripts" / "rename_notes.log"
    renamed = rename_notes(root, args.dry_run, log_path)
    print(f"Done. Renamed {renamed} file(s).")


if __name__ == "__main__":
    main()
