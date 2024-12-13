import json
import asyncio
import threading
import websockets


chat_rooms = {"general": set()}

async def handle_chat(websocket):
    current_chat_room = None
    user_name = None

    try:
        async for raw_message in websocket:
            try:
                message_data = json.loads(raw_message)
            except json.JSONDecodeError:
                error_response = {"error": "Invalid JSON format"}
                await websocket.send(json.dumps(error_response))
                continue

            command = message_data.get("command")
            provided_user_name = message_data.get("username")

            if command == "join_room" and user_name is None:
                user_name = provided_user_name
                room_name = message_data.get("room", "general")
                current_chat_room = room_name

                if room_name not in chat_rooms:
                    chat_rooms[room_name] = set()
                chat_rooms[room_name].add(websocket)

                join_notification = f"{user_name} joined {room_name}"
                await send_to_room(room_name, json.dumps({"message": join_notification}))

            elif command == "send_msg" and user_name == provided_user_name:
                if current_chat_room:
                    user_message = message_data.get("message")
                    if user_message:
                        formatted_message = json.dumps({"username": user_name, "message": user_message})
                        await send_to_room(current_chat_room, formatted_message)

            elif command == "leave_room" and user_name == provided_user_name:
                if current_chat_room:
                    chat_rooms[current_chat_room].discard(websocket)
                    leave_notification = f"{user_name} left {current_chat_room}"
                    await send_to_room(current_chat_room, json.dumps({"message": leave_notification}))
                    current_chat_room = None

            else:
                error_response = {"error": "Unauthorized action or invalid command"}
                await websocket.send(json.dumps(error_response))

    except websockets.ConnectionClosed:
        if current_chat_room:
            chat_rooms[current_chat_room].discard(websocket)


async def send_to_room(room_name, message):
    connected_clients = chat_rooms.get(room_name, set())
    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.ConnectionClosed:
            connected_clients.discard(client)


async def start_websocket_server():
    print("Attempting to start WebSocket server...")
    try:
        async with websockets.serve(handle_chat, "0.0.0.0", 8888):
            print("WebSocket server successfully running on ws://0.0.0.0:8888")
            await asyncio.Future()  # Run forever
    except Exception as e:
        print(f"Failed to start WebSocket server: {e}")