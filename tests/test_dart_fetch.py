"""네트워크 없이 공시 페이지 결합과 오류 처리를 확인한다."""

import unittest
from unittest.mock import patch

from src import dart_fetch


class DartFetchTest(unittest.TestCase):
    def test_all_disclosure_pages_are_included(self):
        pages = [
            {"status": "000", "total_page": 2, "list": [{"rcept_no": "1"}]},
            {"status": "000", "list": [{"rcept_no": "2"}]},
        ]
        with patch.object(dart_fetch, "request_json", side_effect=pages) as request:
            rows = dart_fetch.fetch_disclosures("00126380", "2024")
        self.assertEqual([row["rcept_no"] for row in rows], ["1", "2"])
        self.assertEqual(request.call_count, 2)


if __name__ == "__main__":
    unittest.main()
