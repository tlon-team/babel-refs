import pandas as pd
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv('data.txt', names=['time', 'words'], delim_whitespace=True)

# Convert the 'time' column to datetime format
data['time']= pd.to_datetime(data['time'])

# Set the 'time' column as the index
data.set_index('time', inplace=True)

# Plot the data
plt.figure(figsize=(10,6)) # Optional, to tweak figure size
plt.plot(data['words'])

plt.title('Words over Time')   # Title
plt.xlabel('time')  # X-axis label
plt.ylabel('words')  # Y-axis label

plt.show()
