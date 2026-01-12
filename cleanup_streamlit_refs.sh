#!/bin/bash

echo "🧹 Cleaning up Streamlit references..."

# Remove all references to streamlit in documentation files
find docs/ -name "*.md" -type f | while read -r line; do
  line=$(echo "$line" | sed 's/streamlit//g')
  if [ -n "$line" ]; then
    echo "Removing streamlit reference from: $file"
    sed -i '' "s/streamlit//g"'' "$file"
  fi
done

echo "✅ Streamlit references cleaned up successfully!"
