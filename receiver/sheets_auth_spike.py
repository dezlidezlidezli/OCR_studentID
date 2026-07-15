#!/usr/bin/env python3
"""
sheets_auth_spike.py — CLI smoke-test for the OAuth → Sheets → tick path,
using the same sheets.py the receiver app uses. See SHEETS_SETUP.md.

    # auth + inspect (no writes)
    python3 sheets_auth_spike.py --url "https://docs.google.com/spreadsheets/d/XXXX/edit#gid=0"

    # tick a student (columns by header name OR letter; 'today' auto-detects a date header)
    python3 sheets_auth_spike.py --url "…" --id-col "UID:" --tick-col today \
        --name-col "Full Name:" --student u8221537
"""

import argparse
import sys

import sheets


def main():
    ap = argparse.ArgumentParser(description="OAuth → Sheets tick spike")
    ap.add_argument("--url", required=True, help="Google Sheet URL or spreadsheet ID")
    ap.add_argument("--tab", help="tab name (default: the tab in the URL, else first)")
    ap.add_argument("--id-col", help="ID column: letter, header text")
    ap.add_argument("--tick-col", help="tick column: letter, header text, or 'today'")
    ap.add_argument("--name-col", help="optional name column for feedback")
    ap.add_argument("--student", help="student number to check in (u8221537 or 8221537)")
    args = ap.parse_args()

    try:
        svc = sheets.build_service(interactive=True)
    except Exception as e:
        sys.exit(f"Sign-in failed: {e}")

    sess = sheets.SheetSession(svc)
    info = sess.open(args.url, args.tab)
    print("Spreadsheet:", info["title"])
    print("Tabs:", ", ".join(info["tabs"]))
    print("Using tab:", info["tab"])
    print("Headers:", info["headers"])
    print("Rows:", info["rows"])

    if not (args.student and args.id_col and args.tick_col):
        print("\n(auth + read OK — pass --student, --id-col and --tick-col to test a tick)")
        return

    sess.set_columns(args.id_col, args.tick_col, args.name_col)
    res = sess.check_in(args.student)
    who = res["name"] or sheets.normalize(args.student)
    where = f"row {res['row']}" if res["row"] else "—"
    print(f"\nSTATUS: {res['status']}  ·  {who}  ({where})")


if __name__ == "__main__":
    main()
