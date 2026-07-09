#!/usr/bin/env python3
"""Fetch metadata from Crossref / OpenAlex / Semantic Scholar by DOI."""

import os, json, csv, argparse
from dotenv import load_dotenv
import requests

load_dotenv('.env.local')
CROSSREF_MAILTO = os.getenv('CROSSREF_MAILTO', '')

def fetch_crossref(doi):
    url = f'https://api.crossref.org/works/{doi}'
    headers = {'User-Agent': f'LitMatrix/1.0 (mailto:{CROSSREF_MAILTO})'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        return {'error': str(e)}

def fetch_openalex(doi):
    try:
        r = requests.get(f'https://api.openalex.org/works/doi:{doi}', timeout=15)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        return {'error': str(e)}

def fetch_semantic(doi):
    key = os.getenv('SEMANTIC_SCHOLAR_API_KEY', '')
    headers = {'x-api-key': key} if key else {}
    try:
        r = requests.get(f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}', headers=headers, timeout=15)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser(description='Fetch metadata by DOI')
    parser.add_argument('--input', required=True, help='CSV with DOI column')
    parser.add_argument('--output', required=True, help='Output JSON')
    args = parser.parse_args()

    dois = []
    with open(args.input, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            doi = row.get('doi', '').strip()
            if doi and doi != '10.xxxx/xxxxx':
                dois.append(doi)

    print(f'DOIs to process: {len(dois)}')
    results = {}
    for doi in dois:
        res = {'doi': doi, 'crossref': None, 'openalex': None, 'semantic_scholar': None, 'confidence': 'pending'}
        cr = fetch_crossref(doi)
        if cr and 'error' not in cr:
            res['crossref'] = cr.get('message', {})
            res['confidence'] = 'verified'
        oa = fetch_openalex(doi)
        if oa and 'error' not in oa:
            res['openalex'] = oa
            if res['confidence'] == 'pending':
                res['confidence'] = 'partial'
        ss = fetch_semantic(doi)
        if ss and 'error' not in ss:
            res['semantic_scholar'] = ss
            if res['confidence'] == 'pending':
                res['confidence'] = 'partial'
        if res['confidence'] == 'pending':
            res['confidence'] = 'failed'
        results[doi] = res

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    v = sum(1 for r in results.values() if r['confidence'] == 'verified')
    p = sum(1 for r in results.values() if r['confidence'] == 'partial')
    fl = sum(1 for r in results.values() if r['confidence'] == 'failed')
    print(f'Done. Verified:{v} Partial:{p} Failed:{fl}')

if __name__ == '__main__':
    main()
