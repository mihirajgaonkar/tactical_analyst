SAMPLE_MATCH = {
    "match_id": 1,
    "match_date": "2024-01-01",
    "kick_off": "15:00:00.000",
    "home_score": 2,
    "away_score": 1,
    "match_status": "available",
    "competition": {"competition_id": 11, "competition_name": "Sample Competition"},
    "season": {"season_id": 90, "season_name": "2024"},
    "home_team": {
        "home_team_id": 100,
        "home_team_name": "Home FC",
        "country": {"name": "England"},
    },
    "away_team": {
        "away_team_id": 200,
        "away_team_name": "Away FC",
        "country": {"name": "Spain"},
    },
}

SAMPLE_LINEUPS = [
    {
        "team_id": 100,
        "team_name": "Home FC",
        "lineup": [
            {
                "player_id": 10,
                "player_name": "Home Player",
                "jersey_number": 8,
                "positions": [
                    {
                        "position_id": 13,
                        "position": {"name": "Right Center Midfield"},
                        "from": "00:00",
                        "to": None,
                        "start_reason": "Starting XI",
                    }
                ],
            }
        ],
    },
    {
        "team_id": 200,
        "team_name": "Away FC",
        "lineup": [
            {
                "player_id": 20,
                "player_name": "Away Player",
                "jersey_number": 9,
                "positions": [
                    {
                        "position_id": 23,
                        "position": {"name": "Center Forward"},
                        "from": "00:00",
                        "to": None,
                        "start_reason": "Starting XI",
                    }
                ],
            }
        ],
    },
]

SAMPLE_EVENTS = [
    {
        "id": "event-1",
        "index": 1,
        "period": 1,
        "timestamp": "00:00:01.000",
        "team": {"id": 100, "name": "Home FC"},
        "player": {"id": 10, "name": "Home Player"},
        "type": {"name": "Pass"},
        "possession": 1,
        "play_pattern": {"name": "Regular Play"},
        "location": [60.0, 40.0],
        "pass": {
            "recipient": {"id": 10, "name": "Home Player"},
            "end_location": [72.0, 44.0],
        },
    },
    {
        "id": "event-2",
        "index": 2,
        "period": 1,
        "timestamp": "00:00:05.500",
        "team": {"id": 100, "name": "Home FC"},
        "player": {"id": 10, "name": "Home Player"},
        "type": {"name": "Shot"},
        "possession": 1,
        "play_pattern": {"name": "Regular Play"},
        "location": [108.0, 40.0],
        "shot": {
            "statsbomb_xg": 0.31,
            "outcome": {"name": "Goal"},
            "end_location": [120.0, 40.0],
        },
    },
]
