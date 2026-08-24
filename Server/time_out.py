import time

def execute_command(command):
    try:
        print("Processing...")

        # Giả lập xử lý
        time.sleep(2)

        if command == "stop":
            print("STOP: Command stopped.")
            return

        if command not in ["hello", "test"]:
            raise ValueError("Invalid command!")

        print("Success!")
        print("Output:", command)

    except ValueError as e:
        print("Failed:", e)

    except Exception as e:
        print("Error:", e)


# Demo
command = input("Enter command: ")

execute_command(command)
