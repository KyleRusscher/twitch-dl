import re

from os import path

from twitchdl import twitch, utils
from twitchdl.commands.download import get_clip_authenticated_url
from twitchdl.download import download_file
from twitchdl.exceptions import ConsoleError
from twitchdl.output import print_out, print_clip, print_json


def clips(args):
    if args.json:
        return _clips_json(args)

    if args.download:
        return _clips_download(args)

    return _clips_list(args)


def _continue():
    print_out(
        "\nThere are more clips. "
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


def _clips_json(args):
    clips = twitch.get_channel_clips(args.channel_name, args.period, args.limit)
    nodes = list(edge["node"] for edge in clips["edges"])
    return nodes


def _clip_target_filename(clip):
    url = clip["videoQualities"][0]["sourceURL"]
    _, ext = path.splitext(url)
    ext = ext.lstrip(".")

    match = re.search(r"^(\d{4})-(\d{2})-(\d{2})T", clip["createdAt"])
    date = "".join(match.groups())

    name = "_".join([
        date,
        clip["id"],
        clip["broadcaster"]["login"],
        utils.slugify(clip["title"]),
    ])

    return "{}.{}".format(name, ext)


def _clips_download(args):
    downloaded_count = 0
    generator = twitch.channel_clips_generator(args.channel_name, args.period, 100)

    for clips, _ in generator:
        for clip in clips["edges"]:
            clip = clip["node"]
            url = get_clip_authenticated_url(clip["slug"], "source")
            target = _clip_target_filename(clip)

            if path.exists(target):
                print_out("Already downloaded: <green>{}</green>".format(target))
            else:
                print_out("Downloading: <yellow>{}</yellow>".format(target))
                download_file(url, target)

            downloaded_count += 1
            if args.limit and downloaded_count >= args.limit:
                return


def _clips_list(args):
    print_out("<dim>Loading clips...</dim>")
    generator = twitch.channel_clips_generator(args.channel_name, args.period, args.limit)

    first = 1

    for clips, has_more in generator:
        count = len(clips["edges"]) if "edges" in clips else 0
        last = first + count - 1

        print_out("-" * 80)
        print_out("<yellow>Showing clips {}-{} of ??</yellow>".format(first, last))
        clips = []
        for clip in clips["edges"]:
            clips.append(clip["node"])
        return clips
