# GIST

Command line program to upload or change/update github gists.  In order to work
this program needs an authorization token.

Go to https://github.com/settings/tokens to create a token.  The token can then
be stored into the file `~/.local/gist_token`.

## Example

**Upload a python program with his readme file:**
```
% gist new -f gist.py README.md -d "Upload or update github gists."
Gist ID: c7dfade18834d095a2b2168d35234ae0
Gist URL: https://gist.github.com/0x9900/c7dfade18834d095a2b2168d35234ae0
```

**Update the README file from and existing gist:**
```
% gist update -f README.md --gist-id c7dfade18834d095a2b2168d35234ae0
Gist ID: c7dfade18834d095a2b2168d35234ae0
Gist URL: https://gist.github.com/0x9900/c7dfade18834d095a2b2168d35234ae0
```

**Help:**
```
% gist new --help
usage: gist new [-h] [-f FILE [FILE ...]] [-d DESCRIPTION] [-p]

options:
  -h, --help            show this help message and exit
  -f FILE [FILE ...], --file FILE [FILE ...]
  -d DESCRIPTION, --description DESCRIPTION
  -p, --public

```

```
% gist update --help
usage: gist update [-h] -i GIST_ID [-f FILE]

options:
  -h, --help            show this help message and exit
  -i GIST_ID, --gist-id GIST_ID
  -f FILE, --file FILE
```
