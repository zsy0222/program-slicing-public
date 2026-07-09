#!/usr/bin/env python3
"""Quality check for literature matrix CSV."""

import csv, re, argparse

REQUIRED = [
    "citation_key","title","authors","year","venue","doi",
    "research_question","method","key_findings",
    "relevance_to_my_review","confidence","manual_check_needed"
]

def valid_doi(doi):
    return bool(re.match(r"^10.d{4,}/.+", doi.strip())) if doi.strip() else False

def check(matrix_path, output_path):
    issues = []
    rows = []
    with open(matrix_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            rows.append(row)
            for field in REQUIRED:
                val = row.get(field, "").strip()
                if not val or val == "unknown":
                    issues.append(f"Row {idx}: field \\"" + field + "\\" empty or unknown")
            doi = row.get("doi", "").strip()
            if doi and doi != "unknown" and not valid_doi(doi):
                issues.append(f"Row {idx}: invalid DOI: {doi}")
            quote = row.get("useful_quote", "").strip()
            page = row.get("page_or_section", "").strip()
            if quote and quote != "unknown" and (not page or page == "unknown"):
                issues.append(f"Row {idx}: useful_quote missing page_or_section")
            conf = row.get("confidence", "").strip()
            mc = row.get("manual_check_needed", "").strip()
            if conf == "low" and mc != "yes":
                issues.append(f"Row {idx}: low confidence but manual_check_needed not yes")

    keys = [r.get("citation_key","") for r in rows]
    dois = [r.get("doi","") for r in rows]
    kd = set(k for k in keys if keys.count(k) > 1)
    dd = set(d for d in dois if dois.count(d) > 1)
    if kd: issues.append(f"Duplicate citation_keys: {kd}")
    if dd: issues.append(f"Duplicate DOIs: {dd}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# QA Report for Literature Matrix\n\n")
        f.write(f"Total rows: {len(rows)}\n")
        f.write(f"Issues found: {len(issues)}\n\n")
        for i in issues:
            f.write(f"- {i}\n")
    print(f"QA report: {output_path} ({len(issues)} issues)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QA check for literature matrix")
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--output", default="reports/qa_report.md")
    args = parser.parse_args()
    check(args.matrix, args.output)
