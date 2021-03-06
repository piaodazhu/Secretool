## Architecture

Below is simple architecture of `Secretool`:
```txt
   user <--------------> Secretool <- - - - - - -> remote server
                         (SShell)                     (SServer)
                   [keep secret locally]           [backup safely]
                       <cyphertext>        <cyphertext + encrypted digest>
```

## Secret Shell

`Secretool` is a command line tool, working under interactive mode. Users manage secret zone through `Secret Shell`, or SShell. Only a few commands are supported for core funtions. Unless a user `export` his secret zone to a json file, secret zone is always encrypted on disk. In most case, `Secret Shell` will read and write encrypted secret zone from and to disk, decrypt and edit it in memory. It alse maintains the state of secret zone in command prompt.

Command prompt is like:
```sh
{username}@Secretool:[ {sealed or unsealed} ][ {safer or super} ]{* or null}$> {your command} 
```
- `seal`: a state that you must input password to read, write, export your local secret zone.
- `unseal`: a state that you can manage your local secret zone without password.
- `safer`: a state that no keys are remembered in memory.
- `super`: a state that two keys are remembered in memory and will autofill when needed.
- `*`: means there are unsaved modifies.

For user, only one or two password should be remembered for managing the whole secret zone: `encryption password` and `signing password`. They are ranging from 6 to 16, setting by yourself, mapping to secret key before encrpt the secret zone and digest. Complex passwords are recommanded, but it is really important for yourself to keep them in mind, because no one can encrypt your secrets except who providing these passwords. `encryption password` is necessary and `signing password` is optional.

## Secret server

`Secret server`, or `SServer` is designed for automatically making backup and maintaining versions. User can upload current secret zone to SServer by `push-remote`, see all versions as well as its upload time by `query-remote`, and download any valid version from SServer by `pull-remote [$version]`. If the version to be download is not specified, SServer will provide the latest version of encrypted secret zone.

`SServer` automatically saves the uploaded versions into a file on the disk. The file can be moved from one host to another, without losting any information of users secret. By copying the file and configurate the `Secretool`, secret zone can be backed up in multipoints and recovered from any from them. 

`SServer` maintains encrypted data so it cannot see the users' secret zone. And signatures is introduced to avoid tampering. When `Secretool` downloads a version it will check the signature. If the signature is invalid, the SServer is no longer safe. Anyway, trusted host is recommanded for users to deploy `SServer`.

## Command

```
command             explaination
=============================================
help                print usage of Secretool
quit                quit the Scretool Shell

init                initialize a encrypted secret zone
list [$s]           list all keys under the scope s
add $s $k [-f|s] $v add key-value pair (k,v) in the scope s. -f: v is a filename, -s: v is a sentence
get $s $k           get value of k under scope
delete $s $k        delete key-value pair (k,*) in the scope s
purge $s            purge scope, clear all key-value pairs in and under the scope s

save                save the modified secret zone into disk
export $filename    decrypt and export the secret zone to a cleartext json file
import $filename    import the secret zone from a cleartext json file and encrypt
unseal              switch to the mode where you can read and edit without password
seal                switch to the mode where you must input password to see your secrets

query-remote        query the remote server for historical uploaded encrypted secret zones
pull-remote [$v]    download the encrypted secret zone version $v from the remote server
push-remote         upload current encrypted secret zone to the remote server

reload-server       reload and check remote server configuration from config.json
preload-keys        preload your encryption key and signing key for autofill
clear-keys          clear the keys and cancel autofill
```
