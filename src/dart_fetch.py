"""Open DART 재무·공시 응답을 로컬 데이터 폴더에 저장한다."""

import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://opendart.fss.or.kr/api/"


def request_json(endpoint, params, *, allow_empty=False):
    key = os.environ.get("DART_API_KEY")
    if not key:
        raise ValueError("DART_API_KEY 환경 변수가 필요합니다.")
    url = BASE_URL + endpoint + "?" + urlencode({**params, "crtfc_key": key})
    try:
        with urlopen(Request(url, headers={"User-Agent": "kb-bridge-financial-detective/1.0"}), timeout=20) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"Open DART 요청 실패: {type(error).__name__}") from None

    if data.get("status") == "013" and allow_empty:
        return {"status": "000", "list": [], "total_page": 0}
    if data.get("status") != "000":
        raise RuntimeError(f"Open DART 응답 {data.get('status')}: {data.get('message')}")
    return data


def fetch_disclosures(corp_code, year):
    params = {
        "corp_code": corp_code,
        "bgn_de": f"{year}0101",
        "end_de": f"{year}1231",
        "page_count": 100,
    }
    first = request_json("list.json", {**params, "page_no": 1}, allow_empty=True)
    rows = list(first.get("list", []))
    for page in range(2, int(first.get("total_page", 1)) + 1):
        rows.extend(request_json("list.json", {**params, "page_no": page})["list"])
    return rows


def main():
    parser = argparse.ArgumentParser(description="Open DART 재무·공시 데이터를 로컬에 저장")
    parser.add_argument("corp_code", help="8자리 DART 고유번호")
    parser.add_argument("year", help="사업연도 4자리")
    args = parser.parse_args()
    if not (args.corp_code.isascii() and args.corp_code.isdigit() and len(args.corp_code) == 8):
        parser.error("corp_code는 8자리 숫자여야 합니다.")
    if not (args.year.isascii() and args.year.isdigit() and len(args.year) == 4):
        parser.error("year는 4자리 숫자여야 합니다.")

    finance = request_json(
        "fnlttSinglAcnt.json",
        {"corp_code": args.corp_code, "bsns_year": args.year, "reprt_code": "11011"},
    )
    disclosures = fetch_disclosures(args.corp_code, args.year)
    output = Path(__file__).resolve().parents[1] / "data" / "raw"
    output.mkdir(parents=True, exist_ok=True)
    for kind, data in (("finance", finance), ("disclosures", disclosures)):
        path = output / f"{args.corp_code}_{args.year}_{kind}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{kind}: {len(data.get('list', [])) if kind == 'finance' else len(data)}건 → {path}")


if __name__ == "__main__":
    main()
