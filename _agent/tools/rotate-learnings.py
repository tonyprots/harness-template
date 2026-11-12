#!/usr/bin/env python3
"""Ежемесячная ротация _agent/memory/learnings.md.

Записи за прошлые месяцы уезжают в 06_archive/<дата>-agent-learnings-<год-месяц>.md,
в журнале остаётся текущий месяц и строка-указатель в разделе «Архив».
Запуск из любого места: python3 _agent/tools/rotate-learnings.py
"""
import datetime as dt
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOG = ROOT / "_agent" / "memory" / "learnings.md"
ARCHIVE = ROOT / "06_archive"
ENTRY = re.compile(r"^-\s?(\d{4})-(\d{2})-\d{2}")
SEP = "\n---\n"
ARCHIVE_HEADING = "## Архив\n"


def main() -> int:
    if not (LOG.is_file() and ARCHIVE.is_dir()):
        sys.exit(f"{ROOT} не похож на корень воркспейса (нет журнала или 06_archive) — стоп")
    head, sep, body = LOG.read_text(encoding="utf-8").partition(SEP)
    if not sep:
        sys.exit("нет разделителя '---' между шапкой и записями — ничего не делаю")
    today = dt.date.today()
    current = (today.year, today.month)
    keep, old = [], {}
    for line in body.splitlines():
        m = ENTRY.match(line)
        if m and (int(m[1]), int(m[2])) < current:
            old.setdefault(f"{m[1]}-{m[2]}", []).append(line)
        else:
            keep.append(line)
    if not old:
        print("записей за прошлые месяцы нет")
        return 0
    pointers = []
    for ym, lines in sorted(old.items()):
        target = ARCHIVE / f"{today:%Y-%m-%d}-agent-learnings-{ym}.md"
        with target.open("a", encoding="utf-8") as f:
            if target.stat().st_size == 0:
                f.write(f"# Журнал {ym}\n\nРотация {today:%Y-%m-%d} из `_agent/memory/learnings.md`.\n\n")
            f.write("\n".join(lines) + "\n")
        pointers.append(f"- [{ym}](../../06_archive/{target.name}) — записей: {len(lines)}")
        print(f"{ym}: записей {len(lines)} → {target.relative_to(ROOT)}")
    block = "\n".join(pointers) + "\n"
    pre, found, post = head.partition(ARCHIVE_HEADING)
    if not found:
        pre, post = head.rstrip("\n") + "\n\n", ""
    head = pre + ARCHIVE_HEADING + "\n" + block + post.lstrip("\n")
    LOG.write_text(head + sep + "\n".join(keep).strip("\n") + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
