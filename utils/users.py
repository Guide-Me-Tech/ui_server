import json
import os


def get_users():
    with open("configs/users.json", "r") as f:
        return json.load(f)


def get_api_keys():
    with open("configs/api_keys.json", "r") as f:
        return json.load(f)
