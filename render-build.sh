#!/bin/bash
echo " Build pour Render.com..."

# Backend
echo " Building backend..."
cd backend
pip install -r requirements.txt

# Frontend
echo " Building frontend..."
cd ../frontend
npm ci
npm run build

echo " Build terminé !"