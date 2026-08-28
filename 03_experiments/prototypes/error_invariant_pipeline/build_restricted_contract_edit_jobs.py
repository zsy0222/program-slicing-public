"""G7 feasibility tasks: test contract plus syntax-safe slice-derived edits.

The edit units are complete Java if-blocks selected from dynamic-slice anchors.
The model selects units; it never writes Java text or a source range.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'03_experiments'/'outputs'/'multicase_natural_failure_g1_g3_2026-08-23'/'deepseek_G7_restricted_edit_jobs.jsonl'
JOBS=[
 {'case_id':'Gson_4b_reader','contract':'Without lenient mode, the existing top-level inputs true, false, null, 123, 123.4, and "a" must each be read successfully and then reach END_DOCUMENT. This is automatically extracted from JsonReaderTest.testTopLevelValueTypes.','edits':[{'id':'R1','operation':'delete_complete_if_block','file':'src/main/java/com/google/gson/stream/JsonReader.java','lines':'574-576','effect':'Remove the top-level string-only lenient check.'},{'id':'R2','operation':'delete_complete_if_block','file':'src/main/java/com/google/gson/stream/JsonReader.java','lines':'585-587','effect':'Remove the top-level keyword/number lenient check.'}]},
 {'case_id':'Gson_4b_writer','contract':'Without lenient mode, a new JsonWriter must serialize existing top-level values true, null, 123, 123.4, and "a" exactly as asserted by JsonWriterTest.testTopLevelValueTypes.','edits':[{'id':'W1','operation':'delete_complete_if_block','file':'src/main/java/com/google/gson/stream/JsonWriter.java','lines':'622-625','effect':'Remove the restriction that rejects a first top-level primitive value.'}]}
]
def main():
 s='''You are selecting syntax-safe Java edit operations to satisfy an existing-test behavior contract. Return valid JSON only: {"selected_edit_ids":["..."],"contract_check":"...","uncertainty":"..."}. Select all and only operations needed. You cannot write arbitrary code, change tests, or create operations not listed.'''
 OUT.write_text(''.join(json.dumps({'experiment_group':'G7_contract_restricted_edits','system':s,'user':j},ensure_ascii=False)+'\n' for j in JOBS),encoding='utf-8'); print('Wrote 2 G7 jobs')
if __name__=='__main__':main()
