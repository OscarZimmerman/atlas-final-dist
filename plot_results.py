import pandas as pd
import matplotlib.pyplot as plt
from process import plot_data

# Load combined results
data = pd.read_csv("combined_results.csv")

# Generate and save the plot
print("Generating plot...")
plot_data(data)
plt.savefig("final_plot.png")
print("Plot saved as final_plot.png")