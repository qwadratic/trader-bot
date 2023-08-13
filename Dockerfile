# Use official Python image
FROM python:3.7.7

# Update package lists and install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python-openssl

# Set working directory
WORKDIR /app

# Copy the local code to the container
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Start PostgreSQL server
USER postgres
RUN service postgresql start &&\
    createdb traderbotdb

RUN echo "local all postgres trust" > /etc/postgresql/11/main/pg_hba.conf
RUN echo "host all postgres 127.0.0.1/32 trust" >> /etc/postgresql/11/main/pg_hba.conf
RUN echo "host all postgres ::1/128 trust" >> /etc/postgresql/11/main/pg_hba.conf

RUN service postgresql restart

USER root

# Copy environment configuration
COPY config/.env config/.env

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "start_bot"]
