"""Build equal-case GLM comparison: free full-source repair vs restricted workflow."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'03_experiments'/'outputs'/'glm_pure_vs_new_2026-08-23';JOBS=OUT/'glm_jobs.jsonl'
CASES=[
 ('JacksonDatabind_3b',ROOT/'04_formal_tools/Slicer4J/benchmarks/JacksonDatabind_3b','com.fasterxml.jackson.databind.deser.std.StringArrayDeserializer','TestArrayDeserialization.testStringArray fails: _elementDeserializer is null and getNullValue() is invoked.',[{'id':'J1','operation':'replace_statement','file':'src/main/java/com/fasterxml/jackson/databind/deser/std/StringArrayDeserializer.java','line':66,'replacement':'value = null;'}],'Deserializing existing input [ null ] as String[] must return a non-null one-element array containing null.'),
 ('Gson_4b_reader',ROOT/'04_formal_tools/Slicer4J/benchmarks/Gson_4b/gson','com.google.gson.stream.JsonReader','JsonReaderTest.testTopLevelValueTypes fails: top-level JSON values are rejected unless lenient mode is enabled.',[{'id':'R1','operation':'delete_complete_if_block','file':'src/main/java/com/google/gson/stream/JsonReader.java','lines':'574-576'},{'id':'R2','operation':'delete_complete_if_block','file':'src/main/java/com/google/gson/stream/JsonReader.java','lines':'585-587'}],'Without lenient mode, true, false, null, 123, 123.4, and "a" must each read successfully and reach END_DOCUMENT.'),
 ('Gson_4b_writer',ROOT/'04_formal_tools/Slicer4J/benchmarks/Gson_4b/gson','com.google.gson.stream.JsonWriter','JsonWriterTest.testTopLevelValueTypes fails: a top-level primitive is rejected.',[{'id':'W1','operation':'delete_complete_if_block','file':'src/main/java/com/google/gson/stream/JsonWriter.java','lines':'622-625'}],'Without lenient mode, top-level true, null, 123, 123.4, and "a" must serialize to their tested representations.'),]
def source(case,clazz):
 p=case/'src/main/java'/Path(*clazz.split('.')).with_suffix('.java');lines=p.read_text(encoding='utf-8').splitlines();return str(p.relative_to(case))+'\n'+'\n'.join(f'{p.relative_to(case)}:{i}: {x}' for i,x in enumerate(lines,1))
def main():
 OUT.mkdir(parents=True,exist_ok=True);jobs=[]
 pure='''Repair a Java bug using only the observed failure and complete supplied production class. Return JSON only: {"patches":[{"file":"...","start_line":0,"end_line":0,"replacement":"exact Java"}],"reason":"..."}. Do not modify tests or claim a fixed version.'''
 new='''Select syntax-safe edit operations to satisfy an existing-test behavior contract. Return JSON only: {"selected_edit_ids":["..."],"reason":"..."}. Select all and only required edits; do not write Java, change tests, or invent operations.'''
 for cid,case,clazz,fail,ops,contract in CASES:
  jobs.append({'experiment_group':'P0_glm_pure_full_source_repair','system':pure,'user':{'case_id':cid,'observed_failure':fail,'full_production_class':source(case,clazz)}})
  jobs.append({'experiment_group':'N1_glm_slice_contract_restricted_edit','system':new,'user':{'case_id':cid,'observed_failure':fail,'automatically_extracted_test_contract':contract,'slice_derived_syntax_safe_operations':ops}})
 JOBS.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in jobs),encoding='utf-8');print(f'Wrote {len(jobs)} jobs')
if __name__=='__main__':main()
