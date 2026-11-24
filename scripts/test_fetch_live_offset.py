"""Synthetic live-offset limitations. No network, accounts or TV involved."""
import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))
import fetch_query_log as m


class LiveOffsetTests(unittest.TestCase):
    def test_arrival_repeats_boundary_in_two_offset_pages(self):
        # Three initial events, then a new event arrives at the front.
        live = [{'event': x} for x in ('c', 'b', 'a')]
        def read(host, user, password, limit, offset=0):
            if offset:
                live.insert(0, {'event': 'd'})
            return {'data': live[offset:offset + limit]}
        with patch.object(m, 'fetch_page', side_effect=read):
            data, pages, more = m.fetch_all_pages('http://192.0.2.1', 'u', 'p', 2, 2)
        self.assertEqual([x['event'] for x in data['data']], ['c', 'b', 'b', 'a'])
        self.assertEqual((pages, more), (2, True))

    def test_expiry_can_omit_events_despite_short_final_page(self):
        live = [{'event': x} for x in ('d', 'c', 'b', 'a')]
        def read(host, user, password, limit, offset=0):
            if offset:
                live.pop(0)
            return {'data': live[offset:offset + limit]}
        with patch.object(m, 'fetch_page', side_effect=read):
            data, pages, more = m.fetch_all_pages('http://192.0.2.1', 'u', 'p', 2, 3)
        self.assertEqual([x['event'] for x in data['data']], ['d', 'c', 'a'])
        self.assertEqual((pages, more), (2, False))

    def test_identical_legitimate_events_are_preserved(self):
        event = {'time': '2026-01-01T00:00:00.123456789Z',
                 'client': '192.0.2.5', 'question': {'name': 'same.example', 'type': 'A'}}
        with patch.object(m, 'fetch_page', side_effect=[{'data': [event, event]}, {'data': [event]}]):
            data, pages, more = m.fetch_all_pages('http://192.0.2.1', 'u', 'p', 2, 3)
        self.assertEqual(data['data'], [event, event, event])
        self.assertEqual((pages, more), (2, False))

    def test_multi_page_warning_does_not_depend_on_final_page_fullness(self):
        for more in (False, True):
            with self.subTest(more=more), patch.object(sys, 'argv', [
                    'fetch_query_log.py', '--host', 'http://192.0.2.1', '--user', 'u', '-o', 'unused']), \
                    patch.dict(os.environ, ADGUARD_PASSWORD='synthetic'), \
                    patch.object(m, 'fetch_all_pages', return_value=({'data': []}, 2, more)), \
                    patch.object(m, 'write_private_export'), redirect_stderr(io.StringIO()) as err, \
                    redirect_stdout(io.StringIO()):
                m.main()
                self.assertIn('not a snapshot', err.getvalue())
                self.assertIn('repeat or omit', err.getvalue())
                self.assertNotIn('to be sure', err.getvalue())

    def test_single_page_has_no_cross_page_warning(self):
        with patch.object(sys, 'argv', ['fetch_query_log.py', '--host', 'http://192.0.2.1', '--user', 'u', '-o', 'unused']), \
                patch.dict(os.environ, ADGUARD_PASSWORD='synthetic'), \
                patch.object(m, 'fetch_all_pages', return_value=({'data': []}, 1, False)), \
                patch.object(m, 'write_private_export'), redirect_stderr(io.StringIO()) as err, \
                redirect_stdout(io.StringIO()):
            m.main()
        self.assertEqual(err.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
