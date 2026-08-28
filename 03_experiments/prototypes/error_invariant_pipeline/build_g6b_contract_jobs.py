"""Build the revised G6b: complete existing-test contract + slice-sized repair context."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "03_experiments" / "outputs" / "multicase_natural_failure_g1_g3_2026-08-23" / "deepseek_G6b_contract_jobs.jsonl"
CASES = [
    ("Gson_4b_reader", ROOT / "04_formal_tools" / "Slicer4J" / "benchmarks" / "Gson_4b" / "gson" / "src/main/java/com/google/gson/stream/JsonReader.java", 560, 595,
     "Without lenient mode, each existing top-level input true, false, null, 123, 123.4, and \"a\" must be read as its corresponding value and then END_DOCUMENT. The original failure occurs before true; after removing only that first check, local validation still fails at the existing string input \"a\". This complete contract is automatically summarized from JsonReaderTest.testTopLevelValueTypes.",
     "Remove or revise every top-level-value rejection within this supplied doPeek region; do not change tests."),
    ("Gson_4b_writer", ROOT / "04_formal_tools" / "Slicer4J" / "benchmarks" / "Gson_4b" / "gson" / "src/main/java/com/google/gson/stream/JsonWriter.java", 608, 635,
     "Without lenient mode, a new JsonWriter must serialize the existing top-level values true, null, 123, 123.4, and \"a\" to exactly true, null, 123, 123.4, and \"a\" respectively. This complete contract is automatically summarized from JsonWriterTest.testTopLevelValueTypes.",
     "Keep the existing method signature and callers; revise only the supplied beforeValue body so valid first top-level primitive values are accepted."),
]
def excerpt(path,start,end):
    lines=path.read_text(encoding='utf-8').splitlines(); rel='src/main/java/com/google/gson/stream/'+path.name
    return '\n'.join(f'{rel}:{n}: {lines[n-1]}' for n in range(start,end+1))
def main():
    jobs=[]
    for cid,path,start,end,contract,instruction in CASES:
        jobs.append({'experiment_group':'G6b_full_test_contract_slice_repair','system':'''Repair a Java bug using a complete behavior contract automatically extracted from an existing failing test and a slice-sized method region. Return valid JSON only: {"patches":[{"file":"the supplied file","start_line":0,"end_line":0,"replacement":"exact Java source"}],"constraint_check":"...","uncertainty":"..."}. Use only this material. Do not modify tests, method signatures, or files outside the supplied file. Patches must be non-overlapping and compile.''','user':{'case_id':cid,'automatically_extracted_full_test_contract':contract,'repair_instruction':instruction,'sliced_repair_region':excerpt(path,start,end)}})
    OUT.write_text(''.join(json.dumps(j,ensure_ascii=False)+'\n' for j in jobs),encoding='utf-8'); print(f'Wrote {len(jobs)} G6b jobs')
if __name__=='__main__': main()
