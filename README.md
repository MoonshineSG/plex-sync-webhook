Sync Plex viewed status for "groups". 

Create 2 or more users for individual use and a "group" user. If the "group" has watched a movie/episode, that same movie/episode will be marked "watched" on their individual accounts. 
If all users watched a movie/episode individually, it gets marked "viewed" on the groups account.

Example: a couple has 2 ipads where they watch their own shows and the main TV where they watch together. 

---

Runs on py3

Packages required: yaml, plexapi, flask

`config.yaml` (in the same folder)
 
```
server: http://{your_ip}:32400
group:
  name: GROUP_NAME
  token: GRPOUP_TOKEN
members:
  USER_NAME_1: USER_TOKEN_1
  USER_NAME_2: USER_TOKEN_2
```


Start as service (on port 5005) and the configure as webhook on Plex.


