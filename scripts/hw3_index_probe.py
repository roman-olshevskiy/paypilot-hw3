"""Supplementary offline index comparison; no agent calls or HTTP requests."""
import json
import unittest
from app.rag import retriever


class FixedQueryIndexProof(unittest.TestCase):
    def test_only_index_changes(self):
        query = 'FX conversion spread by tier and free monthly allowance'
        clean = retriever.search(query, top_k=1, index='kb_clean')
        broken = retriever.search(query, top_k=1, index='kb_broken')
        self.assertEqual(clean['query'], broken['query'])
        self.assertEqual(clean['top_k'], broken['top_k'])
        self.assertEqual(clean['fragments'][0]['id'], 'tariffs.md#s2')
        self.assertIn('EUR 5,000', clean['fragments'][0]['text'])
        self.assertEqual(broken['fragments'][0]['id'], 'tariffs.md#b3')
        self.assertTrue(broken['fragments'][0]['text'].endswith('EUR 5'))
        print(json.dumps({'kind': 'offline fixed-query index comparison; not agent run',
                          'query_source': 'cause-broken search call 2', 'clean': clean, 'broken': broken}, indent=2))


if __name__ == '__main__':
    unittest.main()
