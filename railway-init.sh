#!/bin/bash
# Railway initialization script - runs migrations on deployment

echo "Running database migrations..."
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < database.sql
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < migration_add_status.sql
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < migration_2fa.sql
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < add_notifications.sql

echo "Migrations completed!"
