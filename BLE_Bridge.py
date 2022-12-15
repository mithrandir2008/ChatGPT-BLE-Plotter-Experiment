import asyncio, time
from bleak import BleakClient, BleakScanner


def notify_handler(sender, data):
    global time_history, current_time, value1_history, value2_history, value3_history
    # Check that the data is a 20-byte bytearray
    if len(data) != 20:
        print("Received invalid data: incorrect length")
        return

    # Check that the first two bytes of the data match the expected pattern
    if data[0:2] != b"\x01\x02":
        print("Received invalid data: incorrect pattern")
        return

    # Extract the values of value1, value2, and value3 from the data
    value1 = int.from_bytes(data[6:9], byteorder="big", signed=True)
    value2 = int.from_bytes(data[9:12], byteorder="big", signed=True)
    value3 = int.from_bytes(data[12:15], byteorder="big", signed=True)

    # Print the extracted values
    print(f"Received values: value1 = {value1}, value2 = {value2}, value3 = {value3}")



async def main():
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

    # Just wait for events to comeup
    while True:
        await asyncio.wait([    
            asyncio.sleep(5)
        ])
asyncio.run(main())
