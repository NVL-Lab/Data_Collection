from datetime import datetime

# Example float timestamp (seconds since epoch)
float_timestamp = 1726507761.339167  # Replace this with your float value

# Convert the float timestamp back to a datetime object
date_time = datetime.fromtimestamp(float_timestamp)

# Print the result
print("Converted Date and Time:", date_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
