# Use an official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the local code to the container
COPY . .

# Install dependencies, including flask_socketio
RUN pip install flask mysql-connector-python flask_socketio

# Set environment variables if needed (e.g., for DB connection)
ENV MYSQL_HOST=db
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=Root123+
ENV MYSQL_DB=sportlandia

# Run the app
CMD ["python", "app.py"]
