# Secretool: a User-friendly, Lightweight Secret Managment Tool

## Overview

Everyone has some **secrets**:
- passwords from different app/website.
- private key for some advanced purpose.
- some reminders that can't be made known to others.
- just a secret note.

However, keeping your secrets is not free sometimes. Some product is user-friendly but you have to face charging or safety threat. Some product is really hard to deploy. Maybe all you want is a simple, safe, free tool to help your keep your secrets, then **Secretool** can help.

Features:

1. **Easy to deploy.** All you need is python3 and pyDes. And no heavy source code or large binary package.
2. **Easy to use.** A simple shell and just a few commands for you to manage your secrets. Only core functions are implemented instead of making things complicated.
3. **Safe in some way.** It work without saving password or saving cleartext on your disk. Only you who know password can see your secret.
4. **Reliable in some way.** You can deploy your remote server or not. Your remote server will backup your secret without saving any password or cleartext information.
5. **Flexible.** You can easily migrate your secret zone and server anywhere by copy several files. But don't worry about your secret being seen by who don't know your password.

> DES is not safe enough for some advanced environment. But `Secretool` did something to achieve safer secret management.

## Start within a minite

### 1. preparation

```bash
~$ sudo apt install python3 # or other ways
~$ pip3 install pyDes  # or other ways

# then test:
~$ python3
# ...
import pyDes
# no error is ok
```

### 2. configuration

The config file is simple:

```bash
~$ cd $SecretoolPath/src/secretool/
~$ vim config.json
# config your secretool
```

```json
{
    "username":"yourname",
    "servers": [
        {
            "ip":"127.0.0.1",
            "port":9933,
            "token": "xxxx"
        }
    ]
}
```

- `username`: Any name you want. But if you have a remote server, this username should be consistent with server's configuration.
- `servers`: Currently only one remote server is supported. You can ignore below configuration if you don't need any secret server.
- `ip`: your remote server IPv4 address.
- `port`: your remote server serving port. It should be consistent with server's configuration.
- `token`: your token given by remote server. It should be consistent with server's configuration.

If you want to use a secret server, simply configure the server first:


```bash
~$ cd $SecretoolPath/src/remote-server/
~$ vim config.json
# config your server
```

```json
{
    "serveip": "0.0.0.0",
    "serveport": 9933,
    "clientlist": [
        {
            "username": "user1",
            "token": "xxxx"
        },
        {
            "username": "user2",
            "token": "yyyy"
        }
    ]
}
```
`username` and `token` should be consistent with Secretool client.

### 3. start

```bash
# if you want use a secret server. Or skip.
~$ cd $SecretoolPath/src/remote-server/
~$ python3 secretserver.py

# start your Secretool
~$ cd $SecretoolPath/src/secretool/
~$ python3 secretool.py
```

## Manage your first secret

Once you start `secretool.py` successfully, a `Secretool Shell` will be created. Lets manage your first secret without secret server:

```bash
~$ python3 secretool.py 
[Errno 111] Connection refused
run in local mode without remote server. :)
localdb not found! you may pull yours from server later by 'pull', or create one by 'init'.
initiate done. enter help for guidance. :)

user1@Secretool:[ sealed ][ safer ]$> init
This may erase previous secrets. Are you sure to initialize a new secret database?
Enter [yes] or [no]: yes
set <ENCRYPTION PASSWORD> (length between 6 and 16): 
enter the above password again to confirm: 
ok
user1@Secretool:[ sealed ][ safer ]$> add /my/secret first -s 'hello world'    
enter your <ENCRYPTION PASSWORD>: 
ok
user1@Secretool:[ sealed ][ safer ]$> list
enter your <ENCRYPTION PASSWORD>: 
/my/secret: ['first']
user1@Secretool:[ sealed ][ safer ]$> get /my/secret first
enter your <ENCRYPTION PASSWORD>: 
get first under </my/secret>:
hello world
user1@Secretool:[ sealed ][ safer ]$> delete /my/secret first
enter your <ENCRYPTION PASSWORD>: 
ok. delete title=first, val=helloworld...
user1@Secretool:[ sealed ][ safer ]$> list
enter your <ENCRYPTION PASSWORD>: 
user1@Secretool:[ sealed ][ safer ]$> quit
bye bye~ :)
```

In above example, You initialized a secret zone, added a secret (title is first, content is helloworld) under scope <\/my\/secret>. Then you listed all your secret titles with its scopes, and you looked up the secret and got the content. Then you deleted that secret by indicating the scope and title. Finally you quited the Secretool Shell.

That is quit simple. :)

## Take a further step

You can get all supported commands by command `help` inside Secretool Shell. More information can be found in `manual.md`. Here are some useful tips:

- How to add a long sentence with space into secret zone?
    - `add $scope $title -s 'your sentence'`
- How to add a complete file content into secret zone?
    - `add $scope $title -f $filename`
- How to clear all secrets in and under a scope?
    - `purge $scope`
- How to manage your secrets without password temporary?
    - `unseal` switch to the mode where you can read and edit without password
    - `seal` switch to the mode where you must input password to see your secrets
- How to export your secrets in cleartext?
    - `export $filename` you will get a json file
- How to import a well-formed json file instead of initialize a new secret zone?
    - `import $filename`
- How to make use of remote secret server?
    - `query-remote` get all versions information
    - `push-remote` encrypt and update your current secret zone to server as a new version
    - `pull-remote [$version]` download a version from server and check signature. It will cover your current secret zone
    - `reload-server` reload and check remote server configuration from config.json
- How to remember password?
    - `preload-keys` can help. But Secretool won't record passwords after you quit Secretool Shell
    - `clear-keys` will clear remembered keys
