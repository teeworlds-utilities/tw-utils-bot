# tw-utils DIscord Bot

## How to build and run ?

1. Install the dependencies 
- Python3
- Redis
- NodeJS

```bash
python3 -m pip install -r requirements.txt
```

1. Create the file `config.ini` in the repository source using the `config_example.ini`
    - Insert a discord token
    - Complete the fields

2. Execute the file `main.py` with python3 (version <= `3.8`) to start the bot

## Docker

**To download the submodules**
```bash
git submodule init
git submodule update
```

**Launch containers**

You need some environment variables:

- `TW_UTILS_PORT`
- `STORAGE_PATH`
- `REDIS_PASSWORD`

```bash
TW_UTILS_PORT=3000 STORAGE_PATH=./storage REDIS_PASSWORD=super_pass docker-compose up
```
