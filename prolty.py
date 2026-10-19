import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.stats import poisson

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.25)

# Initial lambda value
init_lambda = 4
x = np.arange(0, 50)
y = poisson.pmf(x, init_lambda)

# Plot the initial distribution
bars = ax.bar(x, y, color='#3498db', edgecolor='black')
ax.set_title(f"Poisson Distribution (λ = {init_lambda})", fontsize=14)
ax.set_xlabel("Number of Events (k)", fontsize=12)
ax.set_ylabel("Probability P(X=k)", fontsize=12)
ax.set_ylim(0, 0.4)
ax.set_xlim(-0.5, 40)

# Add a vertical line for the mean/variance
mean_line = ax.axvline(init_lambda, color='#e74c3c', linestyle='dashed', linewidth=2, 
                       label=f'Mean & Variance = {init_lambda}')
ax.legend(fontsize=12)

# Create the slider axis and slider
ax_lambda = plt.axes([0.2, 0.1, 0.6, 0.03])
lambda_slider = Slider(
    ax=ax_lambda,
    label='Lambda (λ)',
    valmin=1,
    valmax=30,
    valinit=init_lambda,
    valstep=1
)

# Update function for when the slider is moved
def update(val):
    current_lambda = lambda_slider.val
    new_y = poisson.pmf(x, current_lambda)
    
    # Update bar heights
    for bar, height in zip(bars, new_y):
        bar.set_height(height)
        
    # Update mean line and labels
    mean_line.set_xdata([current_lambda, current_lambda])
    mean_line.set_label(f'Mean & Variance = {current_lambda}')
    ax.set_title(f"Poisson Distribution (λ = {current_lambda})", fontsize=14)
    ax.legend(fontsize=12)
    
    # Adjust y-axis scaling dynamically as the curve flattens out
    ax.set_ylim(0, max(new_y) + 0.05)
    fig.canvas.draw_idle()

lambda_slider.on_changed(update)
plt.show()