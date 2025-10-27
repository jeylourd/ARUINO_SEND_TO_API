import serial
import requests
import time
import json

# --- CONFIGURATION ---
COM_PORT = 'COM7'  # change if your Arduino uses a different port
BAUD_RATE = 9600
API_URL = "http://localhost/climasapp/backend/public/api/insert-sensor-data.php"
AREA_NAME = "home"  # you can change this to 'office', 'lab', etc.

# --- FUNCTION: Send data to API ---
def send_to_api(data):
    try:
        response = requests.post(API_URL, json=data, timeout=5)
        if response.status_code == 200:
            print("✅ API Response:", response.text)
        else:
            print("⚠️ Server responded with status:", response.status_code)
    except Exception as e:
        print("❌ Error sending to API:", e)

# --- MAIN LOOP ---
def main():
    print("🚀 Starting Arduino → API bridge...")
    print(f"📡 Listening on {COM_PORT} at {BAUD_RATE} baud")

    while True:
        try:
            arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=2)
            print("✅ Connected to Arduino successfully!")
            time.sleep(2)

            while True:
                line = arduino.readline().decode('utf-8').strip()
                if line:
                    print("📥 Raw Data:", line)
                    parts = line.split(',')

                    if len(parts) == 3:
                        try:
                            temp = float(parts[0])
                            hum = float(parts[1])
                            pres = float(parts[2])

                            payload = {
                                "area_name": AREA_NAME,
                                "temperature": temp,
                                "humidity": hum,
                                "pressure": pres
                            }

                            print(f"➡️ Sending → {json.dumps(payload)}")
                            send_to_api(payload)

                        except ValueError:
                            print("⚠️ Invalid numeric data received:", parts)
                    else:
                        print("⚠️ Unexpected data format:", line)

                time.sleep(5)  # wait before reading next line

        except serial.SerialException as e:
            print("❌ Serial connection error:", e)
            print("🔄 Retrying connection in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Exiting program.")
            break

if __name__ == "__main__":
    main()
