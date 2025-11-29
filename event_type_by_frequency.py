# uhhh making visualizations of event types by frequency

# import shtuff
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# load environment variables from .env file
load_dotenv(dotenv_path="scripts/.env")
# get database connection details from environment variables
database_url = os.getenv("DATABASE_URL")

# connect to postgresql database
engine = create_engine(database_url)

# load cleaned data(?)
df = pd.read_sql('SELECT "EVENT_TYPE" FROM storm_events_details_cleaned', engine)

# group by event type and count occurrences
event_counts = df['EVENT_TYPE'].value_counts().sort_values(ascending=False)

# print table just for the lolz
print(event_counts)

# now for the visualization >:)
#-------------------------------------------------------------------------------------

# figure size
plt.figure(figsize=(12, 8))
# bar plot with skyblue color :)
event_counts.plot(kind='bar', color='skyblue')

# title and labels
plt.title('Frequency of Storm Event by Type')
plt.xlabel('Event Type')
plt.ylabel('Number of Occurrences')
plt.xticks(rotation=45, ha='right')

# layout adjustment
plt.tight_layout()
# saved figure (uncomment to save)
# plt.savefig('event_type_by_frequency.png')

# show me da money
plt.show()