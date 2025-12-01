import pandas as pd
import numpy as np
import seaborn as sns
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import plotly.graph_objects as go # so I can hover in the charts


load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

df = pd.read_sql("SELECT * FROM storm_events_details", engine)

print(df.head())

storm_np = df.to_numpy()

missing_values_count = df.isnull().sum() # Checked missing values
print("The missing values per column:")
print(missing_values_count)

num_duplicates = df.duplicated().sum() # Checked all rows for duplicate values
print("The number of duplicate values:", num_duplicates)

# print(df.columns.tolist()) # Shows all the columns
df = df.rename(columns = {"_TYPEEVENT": "EVENT_TYPE"}) # _TYPEEVENT is the EVENT_TYPE just named weird so I fixed it

# Finding the correlation
# # Extract columns as NumPy arrays
# deaths = (df['DEATHS_DIRECT'] + df['DEATHS_INDIRECT']).to_numpy()
# event_type = df['EVENT_TYPE'].to_numpy()

# # Compute correlation matrix (2x2)
# corr_matrix = np.corrcoef(deaths, event_type)

# print(corr_matrix)

fig, ax = plt.subplots(1, 2, figsize = (16, 6))

# Heatmap
columns_to_keep = [20, 21, 22, 23]
column_names = ['INJURIES_DIRECT', 'INJURIES_INDIRECT', 'DEATHS_DIRECT','DEATHS_INDIRECT']

nums_cols = storm_np[:,columns_to_keep].astype(float)
corr_cols = np.corrcoef(nums_cols, rowvar = False)

sns.heatmap(corr_cols, 
            yticklabels = column_names, 
            xticklabels = column_names, 
            ax = ax[0], 
            cmap = 'crest')
ax[0].set_title('Bodily Harm Heatmap')

# Options for Stacked bar chat

# Classic Stacked bar chart with matplotlib
event_types = df['EVENT_TYPE'].to_numpy() 
unique_events = list(dict.fromkeys(event_types))

deaths_direct = df['DEATHS_DIRECT'].to_numpy()
deaths_indirect = df['DEATHS_INDIRECT'].to_numpy()

# Stacked matrix: rows = death type, columns = event types
stack_matrix = np.zeros((2, len(unique_events)))

for i, ev in enumerate(unique_events):
    stack_matrix[0, i] = np.sum(deaths_direct[event_types == ev])
    stack_matrix[1, i] = np.sum(deaths_indirect[event_types == ev])

# Define colors for stacks
death_colors = {
    "Direct": "gold",
    "Indirect": "crimson",
    }

bottom = np.zeros(len(unique_events))

for row, label in enumerate(["Direct", "Indirect"]):
    color = death_colors.get(label, "grey")
    ax[1].bar(
        unique_events,
        stack_matrix[row],
        bottom = bottom,
        color = color,
        label = f"{label} Deaths"
    )
    bottom += stack_matrix[row]

ax[1].set_title("Deaths per Event Type (Stacked)")
ax[1].set_xticklabels([label.replace(" ", "\n") for label in unique_events], rotation = -80, ha = 'left', fontsize = 8) # rotation=-45 : downward left to right, ha='left' : aligns labels with bars, fontsize=8 : reduces size so they fit
ax[1].set_xlabel("Event Type")
ax[1].set_ylabel("Number of Deaths")
ax[1].grid(False)
ax[1].legend(title = "Death Type")

# So it doesn't touch the top
max_height = np.max(np.sum(stack_matrix, axis = 0)) # Calculate maximum height of stacked bars
ax[1].set_ylim(0, max_height * 1.1) # Add a small 10% padding 

# Prevent cutoff & improve spacing
plt.tight_layout()
plt.show()

# Stacked Bar chart 1                                                          with x axis showing Deaths in each Event Type
data = []

data.append(go.Bar(
    x = unique_events,
    y = stack_matrix[0],   # Direct deaths
    name = "Direct Deaths",
    marker_color = "crimson",
    hovertemplate = "<b>%{x}</b><br>Direct Deaths: %{y}<extra></extra>"
))

data.append(go.Bar(
    x = unique_events,
    y = stack_matrix[1],   # Indirect deaths
    name = "Indirect Deaths",
    marker_color = "gold",
    hovertemplate = "<b>%{x}</b><br>Indirect Deaths: %{y}<extra></extra>"
))

fig_plotly = go.Figure(data = data)

fig_plotly.update_layout(
    barmode = "stack",
    title = "Deaths in each Event",
    xaxis_title = "Event Type",
    yaxis_title = "Number of Deaths"
)

fig_plotly.show()

# Stacked Bar chart 2                                                                  with x axis showing Deaths in each State
# Extract states
states = df['STATE'].to_numpy()
unique_states = np.unique(states)

# Build stacked matrix: rows = death type, columns = states
stack_matrix_state = np.zeros((2, len(unique_states)))

for i, st in enumerate(unique_states):
    stack_matrix_state[0, i] = np.sum(deaths_direct[states == st])
    stack_matrix_state[1, i] = np.sum(deaths_indirect[states == st])

# Plot
data = []

data.append(go.Bar(
    x = unique_states,
    y = stack_matrix_state[0],   # Direct deaths
    name = "Direct Deaths",
    marker_color = "crimson",
    hovertemplate = "<b>%{x}</b><br>Direct Deaths: %{y}<extra></extra>"
))

data.append(go.Bar(
    x = unique_states,
    y = stack_matrix_state[1],   # Indirect deaths
    name = "Indirect Deaths",
    marker_color = "gold",
    hovertemplate = "<b>%{x}</b><br>Indirect Deaths: %{y}<extra></extra>"
))

fig = go.Figure(data = data)
fig.update_layout(
    barmode = "stack",
    title = "Deaths in each State",
    xaxis_title = "State",
    yaxis_title = "Number of Deaths",
    xaxis = dict(tickangle = 45) # so it is easier to read
)
fig.show()


# Stacked Bar chart 3                                             with x axis is event type and inside shows each state affected
unique_events = np.unique(df['EVENT_TYPE'])
unique_states = sorted(np.unique(df['STATE']))

data = []

# Direct deaths for each state
for st in unique_states:
    y_values = []
    for ev in unique_events:
        mask = (df['STATE'] == st) & (df['EVENT_TYPE'] == ev)
        y = df.loc[mask, 'DEATHS_DIRECT'].sum()
        y_values.append(y)
    data.append(go.Bar(
        x = unique_events,
        y = y_values,
        name = f"{st} Direct",
        marker_color = "crimson",
        hovertemplate = "<b>%{x}</b><br>State: " + st + "<br>Direct Deaths: %{y}<extra></extra>"
    ))

# Indirect deaths for each state
for st in unique_states:
    y_values = []
    for ev in unique_events:
        mask = (df['STATE'] == st) & (df['EVENT_TYPE'] == ev)
        y = df.loc[mask, 'DEATHS_INDIRECT'].sum()
        y_values.append(y)
    data.append(go.Bar(
        x = unique_events,
        y = y_values,
        name = f"{st} Indirect",
        marker_color = "gold",
        hovertemplate = "<b>%{x}</b><br>State: " + st + "<br>Indirect Deaths: %{y}<extra></extra>"
    ))

# Sort the legend so it is easier to read
data = sorted(
    data,
    key = lambda trace: (
        trace.name.rsplit(' ', 1)[0].lower(),              # state name (case-insensitive)
        (0 if trace.name.endswith('Direct') else 1)          # Direct first, then Indirect
    )
)

fig = go.Figure(data = data)

fig.update_layout(
    barmode = "stack",
    title = {
        "text": "US Disaster Deaths per State",
        "x": 0.5  # <-- centers the title
    },
    xaxis_title = "Disaster Type",
    yaxis_title = "Number of Deaths",
    legend_traceorder = "normal",
    xaxis = dict(categoryorder = "array",        
                    categoryarray = unique_events)  # keep event order stable
)

fig.show()
fig.write_html("StackedBarChart_Interactive.html")