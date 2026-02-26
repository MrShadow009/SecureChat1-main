# TODO - Show Rooms on Left Sidebar

## Task
When a room is created or joined, it should appear in the left sidebar of the website.

## Status
- [x] 1. Room creation API - Working
- [x] 2. Room listing API - Working
- [x] 3. In-memory storage configured

## Notes
- Uses in-memory storage (rooms persist while the server is running)
- On Vercel, rooms will reset after ~10 seconds of inactivity (serverless cold start)
- For local development, this works perfectly
