# Kill any existing python processes for our app
pkill -f "python3 -m src" || true

# Kill any existing nodemon processes
pkill -f nodemon || true

# Start nodemon
bunx nodemon --exec "python3 -m src" -e py --ignore .venv/ --delay 15000