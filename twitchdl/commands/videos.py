from twitchdl import twitch
from twitchdl.exceptions import ConsoleError
from twitchdl.output import print_out, print_video


def _continue():
    print_out(
        "\nThere are more videos. "
        "Press <green><b>Enter</green> to continue, "
        "<yellow><b>Ctrl+C</yellow> to break."
    )

    try:
        input()
    except KeyboardInterrupt:
        return False

    return True


def _get_game_ids(names):
    if not names:
        return []

    game_ids = []
    for name in names:
        print_out("<dim>Looking up game '{}'...</dim>".format(name))
        game_id = twitch.get_game_id(name)
        if not game_id:
            raise ConsoleError("Game '{}' not found".format(name))
        game_ids.append(int(game_id))

    return game_ids


def videos(args):
    game_ids = _get_game_ids(args.game)

    print_out("<dim>Loading videos...</dim>")
    generator = twitch.channel_videos_generator(
        args.channel_name, args.limit, args.sort, args.type, game_ids=game_ids)
    
    first = 1

    for videos, has_more in generator:
        count = len(videos["edges"]) if "edges" in videos else 0
        total = videos["totalCount"]
        last = first + count - 1
        return [video["node"] for video in videos["edges"]]
        
