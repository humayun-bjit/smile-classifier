# Use the official Ubuntu 20.04 as the base image
FROM ubuntu:20.04

# Install necessary packages and add the deadsnakes PPA
RUN apt-get update && \
    apt-get install -y software-properties-common curl && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

# Install Python 3.10 and pip
RUN apt-get install -y python3.10 python3.10-venv python3.10-dev python3.10-distutils && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py

# Install MySQL client and other dependencies
RUN apt-get install -y default-mysql-client

# Set the working directory
WORKDIR /FastAPI

# Copy the project files
COPY . .

# Install Python dependencies from requirements.txt
RUN python3.10 -m pip install --no-cache-dir -r requirements.txt

# Download the wait-for-it script to delay app startup
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# Set environment variables for MySQL connection
ENV MYSQL_HOST=mysql_container
ENV MYSQL_PORT=3306
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=123456
ENV MYSQL_DB=mini_project_fastapi

# Expose the port
EXPOSE 80

# Run the application
#CMD ["python3.10", "main.py"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["wait-for-it", "mysql_container:3306", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]