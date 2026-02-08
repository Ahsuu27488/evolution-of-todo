#!/bin/bash
docker build -t chronos-frontend:latest ./frontend \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  --build-arg NEXT_PUBLIC_APP_URL=http://localhost:3000 \
  --build-arg BETTER_AUTH_URL=http://localhost:3000 \
  --build-arg DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_cXY2EI8DAqhx@ep-fragrant-firefly-ahri4549.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require" \
  --build-arg BETTER_AUTH_SECRET="mlHt/eQkNbw8oSExN56WdGS0dxwBdNGtMtG0XJ7jveE=" \
  --build-arg NEXT_PUBLIC_VAPID_PUBLIC_KEY="BLnlI3_WvJ6cDbDuyen07L4GOcqxPZFAoJJ4z48mvaK3VC2XMSylx6xlTTUTFWTuMyvIoVMZRe43PHubaZXEysY"
