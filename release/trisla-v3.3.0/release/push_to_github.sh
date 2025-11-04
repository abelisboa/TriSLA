#!/bin/bash

echo "🚀 Preparing controlled push to GitHub..."

rm -rf .git

git init

git remote add origin https://github.com/abelisboa/TriSLA.git

git add .

git commit -m "Initial unified TriSLA release"

git branch -M main

git push -u origin main --force

echo "✅ TriSLA repository published successfully"


