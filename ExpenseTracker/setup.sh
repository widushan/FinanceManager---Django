#!/bin/bash
set -e

# Install dependencies
pip install --upgrade pip setuptools
pip install -r requirements.txt

# Run Django commands (from correct path)
python ExpenseTracker/manage.py migrate --noinput
python ExpenseTracker/manage.py collectstatic --noinput
