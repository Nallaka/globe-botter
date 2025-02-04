import json
from math import trunc

import discord
from riotwatcher import LolWatcher, ApiError, RiotWatcher
from riotwatcher import _apis

with open("keys.json", "r") as keys:
    api_keys = json.load(keys)

api_key = api_keys["riot_api"]
region = "americas"
tag = "na1"

riot_watcher = RiotWatcher(api_key)
lol_watcher = LolWatcher(api_key)

def split_riotid(riotid:str):
    riotname, riottag = riotid.split('#', 1)
    if riottag == "":
        riottag = "na1"
    return riotname, riottag.lower()
def get_riot_player(riotid: str):
    name, tag = split_riotid(riotid)
    return riot_watcher.account.by_riot_id("americas", name, tag)

def get_puuid(riotid: str):
    return get_riot_player(riotid)["puuid"]

def get_current_challenge_progress(puuid):

    challenges = lol_watcher.challenges.by_puuid("na1", puuid)["challenges"]

    parsed_challenges = [challenge for challenge in challenges if challenge.get('challengeId') in range(303500,303514)]

    for challenge_id in range(303500,303514):
        if not any(challenge['challengeId'] == challenge_id for challenge in parsed_challenges):
            placeholder_challenge = {
                "challengeId": challenge_id,
                "percentile": 0.0,
                "level": "IRON",
                "value": 0.0,
                "achievedTime": 0
            }
            parsed_challenges.append(placeholder_challenge)

    return parsed_challenges

def parse_regions():
    regions = []
    for region_id in range(303501, 303514):
        challenge_config = lol_watcher.challenges.challenge_config("na1", region_id)
        challenge_name = challenge_config["localizedNames"]["en_US"]["name"]
        region_name = challenge_config["localizedNames"]["en_US"]["description"].replace("As a premade 5, win games with 5 champions from ", "").replace("the ", "")
        regions.append({"challenge_id": region_id, "region_name": region_name, "challenge_name": challenge_name})

    with open('./challenges.json', 'w') as fout:
        json.dump(regions , fout)

def register_player(discord_uname: str, riotid: str):
    player = get_riot_player(riotid)

    challenge_progress = get_current_challenge_progress(player["puuid"])

    player = {
        "riotid": riotid,
        "puuid": player["puuid"],
        "discord": discord_uname,
        "challenges": challenge_progress
    }


    with open("players.json", "r+") as file:

        data = json.load(file)

        if not any(registeredplayer["puuid"] == player["puuid"] for registeredplayer in data):
            data.append(player)

            file.seek(0)

            json.dump(data, file, indent=4)

        else:
            print(f"Player with puuid {player['puuid']} already exists")
            file.seek(0)

            json.dump(data, file, indent=4)
    print("Registered:")
    print(player)


def update_players():
    with open("players.json", "r+") as file:

        players = json.load(file)

        for player in players:
            player["challenges"] = get_current_challenge_progress(player["puuid"])

        file.seek(0)

        json.dump(players, file, indent=4)

def update_player(puuid: str):
    with open("players.json", "r+") as file:

        players = json.load(file)

        for player in players:
            if player["puuid"] == puuid:
                player["challenges"] = get_current_challenge_progress(player["puuid"])

        file.seek(0)

        json.dump(players, file, indent=4)

ranks = {
    "IRON": 1,
    "GOLD": 3,
    "PLATINUM": 6,
    "DIAMOND": 10,
    "MASTERS": 10
}
rank_names = {
    0: 'IRON',
    1: 'GOLD',
    2: 'PLATINUM',
    3: 'DIAMOND',
    4: 'MASTERS'
}

rank_cutoffs = {
    0: 0,
    1: 1,
    2: 3,
    3: 6,
    4: 10
}

def progress_all():
    progress_string = ""
    regions = []
    embeded = discord.Embed()

    with open("challenges.json", "r") as challenges:
        regions = json.load(challenges)

    with open("players.json", "r") as player_list:
        players = json.load(player_list)
        ranksubset = []
        for region in regions:
            progress_string = ""
            #progress_string += region["region_name"] + ":\n"
            region_results = []
            for player in players:
                for challenge in player["challenges"]:
                    if challenge.get('challengeId') == region["challenge_id"]:
                        result = challenge
                        result["player"] = player["riotid"]
                        region_results.append(result)

            for rank, cutoff in reversed(ranks.items()):
                ranksubset = [ranksubset for ranksubset in region_results if ranksubset["level"] == rank]

                for i in range(cutoff, -1, -1):
                    player_string = ""
                    for gamesubset in ranksubset:
                        if int(gamesubset["value"]) == i:
                            player_string += gamesubset["player"] + ", "
                    if player_string != "":
                        progress_string += "\t" + rank + ": "
                        player_string = player_string[:-2]
                        progress_string += f"({i}/{cutoff}): {player_string}\n"
            embeded.add_field(name=f"{region['region_name']}:\n", value=progress_string, inline=False)

        #progress_string += "\nGlobetrotter Progress:\n" + globetrotter_progress()
        embeded2 = discord.Embed()
        embeded2.add_field(name="Globetrotter Progress", value=globetrotter_progress(), inline=False)
        return embeded, embeded2

def progress_call(call):
    progress_string = ""
    regions = []
    embeded = discord.Embed()

    with open("challenges.json", "r") as challenges:
        regions = json.load(challenges)

    with open("players.json", "r") as player_list:
        players = json.load(player_list)
        ranksubset = []
        for region in regions:
            progress_string = ""
            #progress_string += region["region_name"] + ":\n"
            region_results = []
            for player in players:
                if player["discord"] in call:
                    for challenge in player["challenges"]:
                        if challenge.get('challengeId') == region["challenge_id"]:
                            result = challenge
                            result["player"] = player["riotid"]
                            region_results.append(result)

            for rank, cutoff in reversed(ranks.items()):
                ranksubset = [ranksubset for ranksubset in region_results if ranksubset["level"] == rank]

                for i in range(cutoff, -1, -1):
                    player_string = ""
                    for gamesubset in ranksubset:
                        if int(gamesubset["value"]) == i:
                            player_string += gamesubset["player"] + ", "
                    if player_string != "":
                        progress_string += "\t" + rank + ": "
                        player_string = player_string[:-2]
                        progress_string += f"({i}/{cutoff}): {player_string}\n"
            embeded.add_field(name=f"{region['region_name']}:\n", value=progress_string, inline=False)

        #progress_string += "\nGlobetrotter Progress:\n" + globetrotter_progress()
        embeded2 = discord.Embed()
        embeded2.add_field(name="Globetrotter Progress", value=globetrotter_progress(), inline=False)
        return embeded, embeded2

def progress_player(playername):
    progress_string = ""
    regions = []
    embeded = discord.Embed()

    with open("challenges.json", "r") as challenges:
        regions = json.load(challenges)

    with open("players.json", "r") as player_list:
        players = json.load(player_list)
        ranksubset = []
        for region in regions:
            progress_string = ""
            #progress_string += region["region_name"] + ":\n"
            region_results = []
            for player in players:
                for challenge in player["challenges"]:
                    if challenge.get('challengeId') == region["challenge_id"] and player["discord"] == playername:
                        result = challenge
                        result["player"] = player["riotid"]
                        region_results.append(result)

            for rank, cutoff in reversed(ranks.items()):
                ranksubset = [ranksubset for ranksubset in region_results if ranksubset["level"] == rank]

                for i in range(cutoff, -1, -1):
                    player_string = ""
                    for gamesubset in ranksubset:
                        if int(gamesubset["value"]) == i:
                            player_string += gamesubset["player"] + ", "
                    if player_string != "":
                        progress_string += "\t" + rank + ": "
                        player_string = player_string[:-2]
                        progress_string += f"({i}/{cutoff}): {player_string}\n"
            embeded.add_field(name=f"{region['region_name']}:\n", value=progress_string, inline=False)

        #progress_string += "\nGlobetrotter Progress:\n" + globetrotter_progress()
        embeded2 = discord.Embed()
        embeded2.add_field(name="Globetrotter Progress", value=globetrotter_progress(), inline=False)
        return embeded, embeded2

def globetrotter_progress():
    embed = discord.Embed(title="Globetrotter Progress")
    globetrotter = ""
    with open("players.json", "r") as player_list:
        players = json.load(player_list)
        globeplayer = []
        for player in players:
            globetrotter += player["riotid"] + ": "
            globeprog = [globe for globe in player["challenges"] if globe["challengeId"] == 303500]
            globetrotter += f"{int(globeprog[0]['value'])} / 620 ({globeprog[0]['level']})\n"
            globeplayer.append({"name": player["riotid"], "progress": int(globeprog[0]["value"]), "level": globeprog[0]["level"]})
        sorted_globeplayer = sorted(globeplayer, key=lambda d: d['progress'], reverse=True)
        for player in sorted_globeplayer:
            embed.add_field(name=player["name"], value=f"{int(player['progress'])} / 620 ({player['level']})\n", inline=False)
    return embed

cutoffs = [10,6,3,1,-1]
cutoff_value = {
    1: 25,
    3: 15,
    6: 20,
    10: 40
}
def game_value(game_count):
    if game_count == 0:
        return 25
    if game_count >= 10:
        return 0
    cutoff = 99
    for i in cutoffs:
        if i > game_count:
            cutoff = i
    if cutoff - game_count != 0:
        return cutoff_value[cutoff] / (cutoff - game_count)
    return cutoff_value[cutoff]

def optimal_region():
    embed = discord.Embed(title="Optimal Choice")
    with open("challenges.json", "r") as challenges:
        regions = json.load(challenges)

    with open("players.json", "r") as player_list:
        players = json.load(player_list)
        ranksubset = []
        region_results = []
        for region in regions:
            progress_string = ""
            #progress_string += region["region_name"] + ":\n"
            for player in players:
                for challenge in player["challenges"]:
                    if challenge.get('challengeId') == region["challenge_id"]:
                        result = challenge
                        result["player"] = player["riotid"]
                        result["region"] = region["region_name"]
                        region_results.append(result)

        region_values = {
            "Bandle City": 0,
            "Bilgewater": 0,
            "Demacia": 0,
            "Frelijord": 0,
            "Ionia": 0,
            "Ixtal": 0,
            "Noxus": 0,
            "Piltover": 0,
            "Shadow Isles": 0,
            "Shurima": 0,
            "Targon": 0,
            "Void": 0,
            "Zaun": 0,
        }
        for result in region_results:
            print(result["region"])
            region_values[result["region"]] += game_value(int(result["value"]))

        sorted_region_values = {k: v for k, v in sorted(region_values.items(), key=lambda item: item[1], reverse=True)}
        print(sorted_region_values)
        for k,v in sorted_region_values.items():
            embed.add_field(name=k, value=round(v), inline=False)

    return embed

def optimal_region_call(call):
    embed = discord.Embed(title="Optimal Choice")
    with open("challenges.json", "r") as challenges:
        regions = json.load(challenges)

    with open("players.json", "r") as player_list:
        players = json.load(player_list)
        ranksubset = []
        region_results = []
        for region in regions:
            progress_string = ""
            #progress_string += region["region_name"] + ":\n"
            for player in players:
                if player["discord"] in call:
                    for challenge in player["challenges"]:
                        if challenge.get('challengeId') == region["challenge_id"]:
                            result = challenge
                            result["player"] = player["riotid"]
                            result["region"] = region["region_name"]
                            region_results.append(result)

        region_values = {
            "Bandle City": 0,
            "Bilgewater": 0,
            "Demacia": 0,
            "Freljord": 0,
            "Ionia": 0,
            "Ixtal": 0,
            "Noxus": 0,
            "Piltover": 0,
            "Shadow Isles": 0,
            "Shurima": 0,
            "Targon": 0,
            "Void": 0,
            "Zaun": 0,
        }
        for result in region_results:
            #print(result["region"])
            region_values[result["region"]] += game_value(int(result["value"]))
        #print(region_results)
        sorted_region_values = {k: v for k, v in sorted(region_values.items(), key=lambda item: item[1], reverse=True)}
        print(sorted_region_values)
        for k,v in sorted_region_values.items():
            embed.add_field(name=k, value=round(v), inline=False)

    return embed