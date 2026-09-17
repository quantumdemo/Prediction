import csv
import datetime
import io
import logging
import os
from typing import Any, Dict, List, Tuple

import httpx

from services.ml.app.data.adapters.base import BaseAcquisitionAdapter

logger = logging.getLogger("football_ml.data.adapters.football_data_uk")

LEAGUE_MAP = {
    "EPL": {"fd_code": "E0", "country": "ENG", "name": "English Premier League"},
    "LALIGA": {"fd_code": "SP1", "country": "ESP", "name": "Spanish La Liga"},
    "SERIEA": {"fd_code": "I1", "country": "ITA", "name": "Italian Serie A"},
    "BUNDESLIGA": {"fd_code": "D1", "country": "GER", "name": "German Bundesliga"},
    "LIGUE1": {"fd_code": "F1", "country": "FRA", "name": "French Ligue 1"},
}

SEASON_MAP = {
    "2020/2021": "2021",
    "2021/2022": "2122",
    "2022/2023": "2223",
    "2023/2024": "2324",
    "2024/2025": "2425",
    "2018/2019": "1819",
    "2019/2020": "1920",
}

CACHE_DIR = "/tmp/football_data_cache"


class FootballDataUKAdapter(BaseAcquisitionAdapter):
    """
    Acquisition Adapter for Football-Data.co.uk bulk historical match CSV downloads (Stage 6)
    """

    def __init__(self):
        super().__init__(
            source_code="FOOTBALL_DATA_UK",
            source_name="Football-Data.co.uk",
            base_url="https://www.football-data.co.uk/mmz4281",
        )
        os.makedirs(CACHE_DIR, exist_ok=True)

    def build_csv_url(self, season_code: str, fd_league_code: str) -> str:
        return f"{self.base_url}/{season_code}/{fd_league_code}.csv"

    def parse_csv_content(self, csv_text: str) -> List[Dict[str, Any]]:
        records = []
        lines = [line for line in csv_text.splitlines() if line.strip()]
        if not lines:
            return records

        reader = csv.DictReader(io.StringIO("\n".join(lines)))
        for row in reader:
            home = row.get("HomeTeam") or row.get("HT")
            away = row.get("AwayTeam") or row.get("AT")
            date_str = row.get("Date")

            if not home or not away or not date_str:
                continue

            kickoff_dt = self._parse_date(date_str)
            if not kickoff_dt:
                continue

            fthg = self._safe_int(row.get("FTHG") or row.get("HG"))
            ftag = self._safe_int(row.get("FTAG") or row.get("AG"))

            record = {
                "date_str": date_str,
                "kickoff_utc": kickoff_dt,
                "home_team": home.strip(),
                "away_team": away.strip(),
                "home_score": fthg,
                "away_score": ftag,
                "stats": {
                    "home_shots": self._safe_float(row.get("HS")),
                    "away_shots": self._safe_float(row.get("AS")),
                    "home_shots_on_target": self._safe_float(row.get("HST")),
                    "away_shots_on_target": self._safe_float(row.get("AST")),
                    "home_corners": self._safe_float(row.get("HC")),
                    "away_corners": self._safe_float(row.get("AC")),
                    "home_fouls": self._safe_float(row.get("HF")),
                    "away_fouls": self._safe_float(row.get("AF")),
                    "home_yellow_cards": self._safe_float(row.get("HY")),
                    "away_yellow_cards": self._safe_float(row.get("AY")),
                    "home_red_cards": self._safe_float(row.get("HR")),
                    "away_red_cards": self._safe_float(row.get("AR")),
                },
                "raw_row": row,
            }
            records.append(record)

        return records

    def fetch_season_league_data(
        self, comp_code: str, season_label: str
    ) -> Tuple[bool, str, List[Dict[str, Any]], str]:
        if comp_code not in LEAGUE_MAP:
            return False, f"Unknown comp_code '{comp_code}'", [], ""
        if season_label not in SEASON_MAP:
            return False, f"Unknown season_label '{season_label}'", [], ""

        fd_code = LEAGUE_MAP[comp_code]["fd_code"]
        season_code = SEASON_MAP[season_label]
        url = self.build_csv_url(season_code, fd_code)

        cache_filename = os.path.join(CACHE_DIR, f"{comp_code}_{season_code}.csv")
        csv_text = ""

        # Check local cache
        if os.path.exists(cache_filename):
            with open(cache_filename, "r", encoding="utf-8", errors="ignore") as f:
                csv_text = f.read()
        else:
            try:
                with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                    resp = client.get(url)
                    if resp.status_code == 200 and resp.text:
                        csv_text = resp.text
                        with open(cache_filename, "w", encoding="utf-8") as f:
                            f.write(csv_text)
            except Exception as e:
                logger.warning(f"Error fetching {url}: {e}")

        if not csv_text:
            return False, f"Failed fetch for {url}", [], url

        records = self.parse_csv_content(csv_text)
        return True, f"Successfully parsed {len(records)} records", records, url

    def _parse_date(self, date_str: str) -> Any:
        date_str = date_str.strip()
        for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
            try:
                dt = datetime.datetime.strptime(date_str, fmt)
                return dt.replace(tzinfo=datetime.timezone.utc)
            except ValueError:
                pass
        return None

    def _safe_int(self, val: Any) -> Any:
        if val is None or str(val).strip() == "":
            return None
        try:
            return int(float(val))
        except ValueError:
            return None

    def _safe_float(self, val: Any) -> Any:
        if val is None or str(val).strip() == "":
            return None
        try:
            return float(val)
        except ValueError:
            return None
