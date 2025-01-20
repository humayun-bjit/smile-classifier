#!/bin/bash

# Run the MySQL client
mysql -u root -p123456 -h mysql_container -e "SELECT 1;" || exit 1

# Start the application
exec "$@"
