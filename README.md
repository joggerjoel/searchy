# search_short

Searches Serper API for text search. Only prints URLs when the result’s title or snippet contains a date matching the event date from your input file.

## Prerequisites

- Python 3
- [Serper API](https://serper.dev) key

## Setup

1. **Create venv and install dependencies**

   ```bash
   ./setup.sh
   ```

2. **Configure API key**

   Copy `.env.example` to `.env` and set your Serper API key:

   ```bash
   cp .env.example .env
   # Edit .env and set SERPER_API_KEY=your_key
   ```

## Usage

**Run search (default input: `search_short.txt`)**

```bash
./search_short.sh
./search_short.sh path/to/event.txt
```

**Run search and open each result URL in Chrome**

```bash
./search_short.sh --open
./search_short.sh my_event.txt --open
```

**Run Python directly (e.g. on Windows)**

```bash
python search_short.py [file.txt] [--open]
```

## Input file

Put your event text in a file (e.g. `search_short.txt`). The script:

- Uses the first line (or first 3 lines if short) as the search query.
- Parses an event date from the file and only shows results whose title/snippet contain that date.

## Sites searched

- dice.fm  
- taogroup.com  
- ra.co  
- eventbrite.com  
- universe.com  
- posh.vip  
- shotgun.live  
- crowdvolt.com  

## License

Unlicensed.
# searchy
