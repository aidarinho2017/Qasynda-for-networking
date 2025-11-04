#!/bin/bash
# build_files.sh

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🧱 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗃️ Applying database migrations..."
python manage.py migrate

echo "✅ Build complete!"
