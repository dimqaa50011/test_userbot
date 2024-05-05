from argparse import ArgumentParser

from src.tools.cli.create_bot import add_bot

parser = ArgumentParser()
subparser = parser.add_subparsers()


create_bot = subparser.add_parser("add_bot")
create_bot.set_defaults(func=add_bot)


args = parser.parse_args()

args.func()
