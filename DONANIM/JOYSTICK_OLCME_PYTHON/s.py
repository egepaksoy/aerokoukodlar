import serial
import time

def send_to_arduino(ser, data):
    ser.write(data.encode('utf-8'))
    print(f"{data}")

def main():
    # Specify the COM port and baud rate
    com_port = "COM5"  # Replace with your Arduino's COM port
    baud_rate = 9600    # Match the baud rate of your Arduino

    try:
        # Establish a serial connection
        ser = serial.Serial(com_port, baud_rate, timeout=1)
        print(f"Connected to {com_port} at {baud_rate} baud.")

        while True:
            data = "10|10\n"

            start_time = time.time()
            while True:
                send_to_arduino(ser, data)
                if time.time() - start_time >= 2:
                    break

            data = "1000|1000\n"

            start_time = time.time()
            while True:
                send_to_arduino(ser, data)
                if time.time() - start_time >= 2:
                    break

    except serial.SerialException as e:
        print(f"Error: {e}")

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
