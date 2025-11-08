#!/bin/bash
# National Highways Management System - Database Setup Script for Linux/Mac
# This script sets up the complete database system

echo "========================================"
echo "NH Management System - Database Setup"
echo "========================================"
echo ""

# Configuration
DB_HOST="localhost"
DB_USER="root"
DB_NAME="nh_management"

# Prompt for password
read -sp "Enter MySQL root password: " DB_PASSWORD
echo ""
echo ""

# Step 1: Create database
echo "Step 1: Creating database..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create database"
    exit 1
fi

echo "SUCCESS: Database created"
echo ""

# Step 2: Create schema
echo "Step 2: Creating schema (tables, indexes, constraints)..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < database_schema.sql

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create schema"
    exit 1
fi

echo "SUCCESS: Schema created"
echo ""

# Step 3: Create triggers
echo "Step 3: Creating triggers..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < triggers.sql

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create triggers"
    exit 1
fi

echo "SUCCESS: Triggers created"
echo ""

# Step 4: Create views and procedures
echo "Step 4: Creating views and stored procedures..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < validation_queries.sql

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create views and procedures"
    exit 1
fi

echo "SUCCESS: Views and procedures created"
echo ""

# Step 5: Load sample data
echo "Step 5: Loading sample data..."
read -p "Do you want to load sample data? (y/n): " LOAD_SAMPLE

if [[ "$LOAD_SAMPLE" == "y" || "$LOAD_SAMPLE" == "Y" ]]; then
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < sample_data.sql
    
    if [ $? -ne 0 ]; then
        echo "WARNING: Failed to load sample data"
    else
        echo "SUCCESS: Sample data loaded"
    fi
else
    echo "Skipping sample data..."
fi

echo ""

# Step 6: Verify installation
echo "Step 6: Verifying installation..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES;"

if [ $? -ne 0 ]; then
    echo "ERROR: Database verification failed"
    exit 1
fi

echo ""
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo ""
echo "Database: $DB_NAME"
echo "Host: $DB_HOST"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and update configuration"
echo "   cp .env.example .env"
echo "2. Install Python dependencies:"
echo "   pip install -r requirements.txt"
echo "3. Run the application:"
echo "   python nh_management.py"
echo ""
echo "For more information, see README.md"
echo ""
