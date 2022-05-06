import argparse
import sys
from data import db_session
from model_workers.user import UserModelWorker
from tools.errors import UserNotFoundError

main_parser = argparse.ArgumentParser()
main_parser.add_argument("command", choices=[
    "give_admin_rights",
    "revoke_admin_rights"
])
main_args = main_parser.parse_args(sys.argv[1:2])
db_session.global_init("db/articles.db")
if main_args.command == "give_admin_rights":  # Выдача прав администратора
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", dest="user_id", type=int, required=True)
    args = parser.parse_args(sys.argv[2:])
    try:
        UserModelWorker.give_admin_rights(args.user_id)
    except UserNotFoundError:
        print(f"User {args.user_id} not found")
    else:
        print("Success")
elif main_args.command == "revoke_admin_rights":  # Лишение прав администратора
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", dest="user_id", type=int, required=True)
    args = parser.parse_args(sys.argv[2:])
    try:
        UserModelWorker.revoke_admin_rights(args.user_id)
    except UserNotFoundError:
        print(f"User {args.user_id} not found")
    else:
        print("Success")
