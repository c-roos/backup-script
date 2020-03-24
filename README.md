# backup-script
Python script that automatically backs up SQLite databases to Google Drive

## How to use
backup.py is called from the command line like so:

```$ python3 backup.py credentials.json folder_name data1.db data2.db``` 

where: 
- `credentials.json` is the json file containing your service account credentials
- `folder_name` is the name of a folder in your Google Drive that has been shared with your service account
- `data1.db data2.db...` is one or more names of SQLite databases you wish to backup
- optional flag `--interval` or `-i` indicates a number of seconds to wait between backups. Default = 86400
- optional flag `--delay` or `-d` indicates of number of seconds to wait before making the intial backup. Default = 0

For example:

```$ python3 backup.py my_creds.json Backups customers.db -i 3600 -d 600```

would back up customers.db to a Google Drive folder callerd "Backups" every hour starting 10 minutes after being called.

```$ python3 backup.py my_creds.json store_backups users.db transactions.db```

would back up users.db and transactions.db to a Google Drive folder called "store_backups" every day starting immediately.
