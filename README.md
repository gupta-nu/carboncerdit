# Carbon Credit Tracker
A simple REST API for tracking carbon credits from creation to retirement. Built for Offset internship assigment.

# questions

### How did you design the ID so it's always the same for the same input?

Basically I used SHA256 hashing but had to normalize the input first.tricky parts where like  making sure "Solar Farm" and "solar farm" would produce the same hash.
So before hashing i did the following: 
- Trim whitespace and make everything lowercase
- Fix unicode stuff (honestly not sure if this was needed but thought to be better safe than sorry)
- Round quantities to 4 decimal places so 10 and 10.0000 are the same
- Smash all fields together with | seperator: `"project|registry|vintage|quantity|serial"`
- SHA256 hash that string

it took me little time to figure out the rounding part, i kept getting different IDs for what should be the same record.

### Why did you use an event log instead of updating the record directly?

understood how banks track transactions on a high level,they never delete anything, just add new entries.so for carbon credits this made sense to me too since
- You need to prove what happend and when (regulatory stuff)
- If someone claims fraud you have the full history
- Can't accidentally lose data by overwriting
- Easy to see the complete lifecyle of each credit

Plus if I just did updates,I  wouldnt know when something was retired vs sold,The event log keeps track of everything that ever happened to a credit.

### If two people tried to retire the same credit at the same time, what would break?
so for this race condition, both users would:
- Check if credit is retired (both see no)
- Both create RETIRED events at same time
- resulting in  two retirement events for same credit
so this gave double selling ,which contradicts the whole point of carbon credits 

### How would you fix it?
i looked into how i would fix this and decided to go with adding database contraints, to the event model
```python
UniqueConstraint('record_id', 'event_type', name='uq_record_retired')
```
so even if both requests hit at the same time, only one retired event can exist per record, second one fails with a contraint error which i can catch and return 409




## What it does

This API manages carbon credit records and tracks thier lifecycle through events. Each credit goes through: created → sold → retired, and nothing ever gets deleted to maintain transparancy.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

## API Endpoints

- `POST /records` - Create a new carbon credit record
- `GET /records/{id}` - Get record details with full event history  
- `POST /records/{id}/retire` - Retire a carbon credit

## Testing

```bash
python test_api.py
```

(Or visit http://127.0.0.1:8000/docs for interactive API documentation.)

## Database

 SQLite by default (`carbon_credits.db`). Can easily switch to PostgreSQL by changing the DATABASE_URL.

