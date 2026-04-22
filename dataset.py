import requests
import csv
import time
import os
import random
from collections import deque

API_KEY = ""

PLATFORM_REGION = "sg2"
ROUTING_REGION = "sea"

HEADERS = {
    "X-Riot-Token": API_KEY
}

MAX_MATCHES = 2000
MATCHES_PER_PLAYER = 10
PLAYERS_PER_DIVISION = 30

OUTPUT_FILE = "sg2_match_dataset.csv"

def riot_get(url):
    while True:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)

            if r.status_code == 200:
                return r.json()

            elif r.status_code == 429:
                print("Rate limited... waiting 5 sec")
                time.sleep(5)

            else:
                print("HTTP Error:", r.status_code)
                return None

        except requests.exceptions.RequestException as e:
            print("Connection issue:", e)
            time.sleep(5)



def load_existing_matches():
    matches = set()

    if not os.path.exists(OUTPUT_FILE):
        return matches

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            matches.add(row["match_id"])

    return matches


def append_rows(rows):
    file_exists = os.path.exists(OUTPUT_FILE)

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "match_id",
                "puuid",
                "champion",
                "win",
                "kills",
                "deaths",
                "assists",
                "gold",
                "level",
                "lane",
                "damage",
                "vision",
                "cs",
                "timePlayed"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)



def get_seed_players():
    tiers = ["SILVER", "GOLD", "PLATINUM", "EMERALD"]
    divisions = ["I", "II", "III", "IV"]

    final_players = []

    for tier in tiers:
        for div in divisions:

            url = (
                f"https://{PLATFORM_REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{div}"
            )

            data = riot_get(url)

            division_players = []

            if data:
                for entry in data:
                    division_players.append(entry["puuid"])

            # remove duplicates
            division_players = list(set(division_players))

            sample_size = min(
                PLAYERS_PER_DIVISION,
                len(division_players)
            )

            selected = random.sample(
                division_players,
                sample_size
            )

            final_players.extend(selected)

            print(tier, div, "selected:", len(selected))

            time.sleep(1)

    return final_players



def get_match_ids(puuid):
    url = (
        f"https://{ROUTING_REGION}.api.riotgames.com"
        f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        f"?start=0&count={MATCHES_PER_PLAYER}"
    )

    data = riot_get(url)

    return data if data else []



def get_match_details(match_id):
    url = (
        f"https://{ROUTING_REGION}.api.riotgames.com"
        f"/lol/match/v5/matches/{match_id}"
    )

    return riot_get(url)

def build_dataset():

    # queue of players to process
    player_queue = deque(get_seed_players())

    # duplicate prevention
    visited_players = set()
    queued_players = set(player_queue)
    visited_matches = load_existing_matches()

    print("Seed players:", len(player_queue))
    print("Existing matches:", len(visited_matches))

    while player_queue and len(visited_matches) < MAX_MATCHES:

        puuid = player_queue.popleft()
        queued_players.discard(puuid)

        # already processed player?
        if puuid in visited_players:
            continue

        visited_players.add(puuid)

        match_ids = get_match_ids(puuid)

        for match_id in match_ids:

            # already saved match?
            if match_id in visited_matches:
                continue

            match = get_match_details(match_id)

            if not match:
                continue

            info = match["info"]
            participants = info["participants"]
            duration = info["gameDuration"]

            rows = []

            for p in participants:

                rows.append({
                    "match_id": match_id,
                    "puuid": p["puuid"],
                    "champion": p["championName"],
                    "win": p["win"],
                    "kills": p["kills"],
                    "deaths": p["deaths"],
                    "assists": p["assists"],
                    "gold": p["goldEarned"],
                    "level": p["champLevel"],
                    "lane": p.get("teamPosition", ""),
                    "damage": p["totalDamageDealtToChampions"],
                    "vision": p["visionScore"],
                    "cs": p["totalMinionsKilled"] + p.get("neutralMinionsKilled", 0),
                    "timePlayed": duration
                })

                new_player = p["puuid"]

                # prevent duplicate queue players
                if (
                    new_player not in visited_players
                    and new_player not in queued_players
                ):
                    player_queue.append(new_player)
                    queued_players.add(new_player)

            append_rows(rows)

            visited_matches.add(match_id)

            print(
                f"Matches: {len(visited_matches)}/{MAX_MATCHES} | "
                f"Players done: {len(visited_players)} | "
                f"Queue: {len(player_queue)}"
            )

            if len(visited_matches) >= MAX_MATCHES:
                break

            time.sleep(1)

    print("Finished. Saved to", OUTPUT_FILE)



build_dataset()