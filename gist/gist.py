#!/usr/bin/env python
"""
Command line program to upload or change/update github gists.
In order to work this program needs an authorization token.
Go to https://github.com/settings/tokens to create a token.
The token can then be stored into the file ~/.local/gist_token.
"""

import argparse
import json
import os
import sys
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

GITHUB_STATUS = {
  200: "OK",
  201: "Created",
  304: "Not modified",
  403: "Forbidden",
  404: "Resource not found",
  422: "Validation failed, or the endpoint has been spammed.",
}

GITHUB_API = "https://api.github.com"
GIST_TOKEN = "~/.local/gist_token"


def load_content(filename: str) -> str:
  """Download the content"""
  with open(filename, 'r', encoding='utf-8') as fdi:
    return fdi.read()


def error_exit(text: str) -> None:
  """Print the error message and exit and an error code"""
  data = json.loads(text)
  message = data.get('message', 'Undefined Error')
  print(f'Gist error: {message}', file=sys.stderr)
  sys.exit(os.EX_OSERR)


def upload_gist(token: str, filelist: str, description: str, public: str) -> None:
  """Upload file to gist"""
  url = GITHUB_API + "/gists"
  files = {os.path.basename(fname): {"content": load_content(fname)} for fname in filelist}

  headers = {
    "Content-Type": "application/vnd.github+json",
    "Accept": "application/vnd.github+json",
    'Authorization': f'token {token}',
  }
  payload = {
    "description": description,
    "public": public,
    "files": Any,
  }
  payload["files"] = files

  jsondata = json.dumps(payload)
  req = Request(url, headers=headers, data=jsondata.encode('utf-8'))
  try:
    with urlopen(req) as response:
      if response.status != 201:
        raise IOError(GITHUB_STATUS[response.status])
      charset = response.headers.get_content_charset()
      resp = response.read()
  except HTTPError as err:
    raise IOError(GITHUB_STATUS[err.code] if err.code in GITHUB_STATUS else err.msg) from None

  json_response = json.loads(resp.decode(charset))
  print("Gist ID:", json_response['id'])
  print("Gist URL:", json_response['html_url'])


def commit_gist(token: str, gist_id: str, filename: str) -> None:
  """Update an existing gist"""
  url = GITHUB_API + f"/gists/{gist_id}"
  content = load_content(filename)
  headers = {
    "Content-Type": "application/vnd.github+json",
    "Accept": "application/vnd.github+json",
    'Authorization': f'token {token}',
  }
  payload = {
    "files": {
      f"{filename}": {
        "content": f"{content}"
      }
    }
  }

  jsondata = json.dumps(payload)
  req = Request(url, headers=headers, data=jsondata.encode('utf-8'))
  try:
    with urlopen(req) as response:
      if response.status != 200:
        raise IOError(GITHUB_STATUS[response.status])
      charset = response.headers.get_content_charset()
      resp = response.read()
  except HTTPError as err:
    raise IOError(GITHUB_STATUS[err.code] if err.code in GITHUB_STATUS else err.msg) from None

  json_response = json.loads(resp.decode(charset))
  print("Gist ID:", json_response['id'])
  print("Gist URL:", json_response['html_url'])


def new_gist(token: str, opts: argparse.Namespace) -> None:
  """Handle new gist form the command line"""
  # first we check if all the files exist.
  for fname in opts.file:
    if not os.path.exists(fname):
      print(f'File "{fname}" Not Found', file=sys.stderr)
      sys.exit(os.EX_OSFILE)
  upload_gist(token, opts.file, opts.description, opts.public)


def update_gist(token: str, opts: argparse.Namespace) -> None:
  """Handles the update gist from the command line"""
  if not os.path.exists(opts.file):
    print(f'File "{opts.file}" Not Found', file=sys.stderr)
    sys.exit(os.EX_OSFILE)
  commit_gist(token, opts.gist_id, opts.file)


def list_gist(*_: Any) -> None:
  url = GITHUB_API + "/users/0x9900/gists"
  req = Request(url)
  try:
    with urlopen(req) as response:
      if response.status != 200:
        raise IOError(GITHUB_STATUS[response.status])
      charset = response.headers.get_content_charset()
      resp = response.read()
  except HTTPError as err:
    raise IOError(GITHUB_STATUS[err.code] if err.code in GITHUB_STATUS else err.msg) from None

  json_response = json.loads(resp.decode(charset))
  for gist in json_response:
    print(gist['html_url'])
    for file in gist['files'].values():
      print(f"\t| {file['filename']}\t{file['size']}\t{file['type']}")
    print("")


def load_token() -> str:
  """Download the token from GIST_TOKEN"""
  token_file = os.path.expanduser(GIST_TOKEN)
  try:
    with open(token_file, 'r', encoding='utf-8') as fdt:
      token = fdt.read().strip()
  except FileNotFoundError as err:
    print(err, file=sys.stderr)
    sys.exit(os.EX_OSFILE)
  return token


def main() -> int:
  """Everyone knows main. We need to start somewhere"""
  token = load_token()
  parser = argparse.ArgumentParser(description="RigExpert")
  subparsers = parser.add_subparsers(required=True)
  p_new = subparsers.add_parser('new')
  p_new.set_defaults(func=new_gist)
  p_new.add_argument('-f', '--file', nargs='+')
  p_new.add_argument('-d', '--description')
  p_new.add_argument('-p', '--public', action="store_false", default=True)
  p_update = subparsers.add_parser('update')
  p_update.set_defaults(func=update_gist)
  p_update.add_argument('-i', '--gist-id', required=True)
  p_update.add_argument('-f', '--file')
  p_list = subparsers.add_parser('list')
  p_list.set_defaults(func=list_gist)

  opts = parser.parse_args()
  try:
    opts.func(token, opts)
  except IOError as err:
    print(f"Error: {err}", file=sys.stderr)
    return os.EX_DATAERR

  return os.EX_OK


if __name__ == "__main__":
  sys.exit(main())
