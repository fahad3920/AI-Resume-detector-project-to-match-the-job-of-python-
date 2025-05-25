# PowerShell script to start Flask server and run test script sequentially

# Start Flask server in a new window
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd "D:\resume matcher project"; python app.py'

# Wait for user to start the server manually and press Enter to continue
Read-Host "Press Enter after the Flask server is running..."

# Run the test script
cd "D:\resume matcher project"
python test_sequence.py
