import asyncio, time
from bleak import BleakClient, BleakScanner
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# Define global variables to store the data and the time
time_history = []
value1_history = []
value2_history = []
value3_history = []
counter = 0


# Create the line chart using matplotlib
plt.ion()

fig, ax = plt.subplots()
ani = []
line1, = ax.plot([0], [1], label="Value1")
line2, = ax.plot([0], [2], label="Value2")
line3, = ax.plot([0], [3], label="Value3")
ax.legend()
ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Value")


def notify_handler(sender, data):
    global time_history, current_time, value1_history, value2_history, value3_history, counter
    # Check that the data is a 20-byte bytearray
    if len(data) != 20:
        print("Received invalid data: incorrect length")
        return

    # Check that the first two bytes of the data match the expected pattern
    if data[0:2] != b"\x01\x02":
        print("Received invalid data: incorrect pattern")
        return

    counter+=1
    if(counter > 220):
        print("Hit")
        counter=0
    # Extract the values of value1, value2, and value3 from the data
    value1 = int.from_bytes(data[6:9], byteorder="big", signed=True)
    value2 = int.from_bytes(data[9:12], byteorder="big", signed=True)
    value3 = int.from_bytes(data[12:15], byteorder="big", signed=True)


    # Get the current time
    current_time = time.time()

    # Append the extracted values and the current time to the history
    time_history.append(current_time)
    value1_history.append(value1)
    value2_history.append(value2)
    value3_history.append(value3)

    # Print the extracted values
    # print(f"Received values: value1 = {value1}, value2 = {value2}, value3 = {value3}")

async def update_chart():
    global time_history, value1_history, value2_history, value3_history, ax, fig

    time_history_plot = time_history[-440:]
    value1_history_plot = value1_history[-440:]
    value2_history_plot = value2_history[-440:]
    value3_history_plot = value3_history[-440:]

    # make sure our window is on the screen and drawn
    plt.show(block=False)
    plt.pause(.1)

    while True:


        # Limit the length of the history to 1000
        time_history_plot = time_history[-440:]
        value1_history_plot = value1_history[-440:]
        value2_history_plot = value2_history[-440:]
        value3_history_plot = value3_history[-440:]

        # Update the line chart with the new data
        ax.cla()
        ax.plot(time_history_plot, value1_history_plot, label="Value1")
        ax.plot(time_history_plot, value2_history_plot, label="Value2")
        ax.plot(time_history_plot, value3_history_plot, label="Value3")

        plt.pause(0.001)
        # Sleep for 0.1 seconds before updating again
        await asyncio.sleep(0.03)






async def main():
    global fig
    # Scan for devices
    print("Scanning for devices...")
    scanner = BleakScanner()
    devices = await scanner.discover(timeout=2)

    # Print a list of discovered devices
    for i, device in enumerate(devices):
        print("{}. {} - {}".format(i+1, device.name, device.address))

    # Prompt the user to select a device
    device_number = int(input("Enter the number of the device to connect to: "))
    selected_device = devices[device_number-1]

    # Create a BleakClient from the device address
    client = BleakClient(selected_device.address)

    # Connect to the device
    await client.connect()

    # Discover the characteristics of the device
    print("Discovering characteristics with notifications...")
    notifiable_characteristics = []
    i=0
    for characteristics in client.services.characteristics:
        if client.services.get_characteristic(characteristics).properties[0] == 'notify':
            print("{}. {}".format(i+1, client.services.get_characteristic(characteristics)))
            notifiable_characteristics.append(characteristics)
            i+=1

    # Prompt the user to select a characteristic
    characteristic_number = int(input("Enter the number of the characteristic to use: "))
    selected_characteristic = notifiable_characteristics[characteristic_number-1]

    # Enable notifications for the selected characteristic
    await client.start_notify(selected_characteristic, notify_handler)

    # Schedule the update_chart task to run in the background
    asyncio.create_task(update_chart())

    # Just wait for events to comeup
    while True:
        await asyncio.sleep(0.1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
