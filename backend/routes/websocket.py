from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from datetime import datetime
import asyncio
import json
from database import AsyncSessionLocal
from models.device_session import DeviceSession
from models.booth import Booth

router = APIRouter(tags=["WebSocket"])

# Store active connections per device_id
active_connections: dict[str, WebSocket] = {}

# Store active admin connections
admin_connections: list[WebSocket] = []


async def get_db_session():
    """Get database session for WebSocket."""
    async with AsyncSessionLocal() as session:
        yield session


@router.websocket("/ws/device/{device_id}")
async def device_websocket(websocket: WebSocket, device_id: str):
    """
    WebSocket endpoint for device real-time communication.
    Used for kick mechanism and heartbeat.
    """
    await websocket.accept()
    active_connections[device_id] = websocket

    try:
        # Send initial connection confirmation
        await websocket.send_json(
            {
                "type": "connected",
                "device_id": device_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Start heartbeat task
        heartbeat_task = asyncio.create_task(heartbeat_sender(websocket, device_id))

        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                if message.get("type") == "heartbeat":
                    # Update heartbeat in database
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(
                            select(DeviceSession).where(
                                DeviceSession.device_id == device_id
                            )
                        )
                        device_session = result.scalar_one_or_none()

                        if device_session:
                            device_session.last_heartbeat = datetime.utcnow()
                            await db.commit()

                    # Send heartbeat acknowledgment
                    await websocket.send_json(
                        {
                            "type": "heartbeat_ack",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                elif message.get("type") == "get_booth":
                    # Get booth info
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(
                            select(DeviceSession).where(
                                DeviceSession.device_id == device_id
                            )
                        )
                        device_session = result.scalar_one_or_none()

                        if device_session and device_session.booth_id:
                            result = await db.execute(
                                select(Booth).where(Booth.id == device_session.booth_id)
                            )
                            booth = result.scalar_one_or_none()

                            if booth:
                                await websocket.send_json(
                                    {
                                        "type": "booth_info",
                                        "booth": {
                                            "id": str(booth.id),
                                            "name": booth.name,
                                            "location": booth.location,
                                            "config": booth.config,
                                        },
                                    }
                                )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid JSON format"}
                )

    except WebSocketDisconnect:
        print(f"Device {device_id} disconnected")
    except Exception as e:
        print(f"WebSocket error for device {device_id}: {e}")
    finally:
        # Clean up
        if device_id in active_connections:
            del active_connections[device_id]

        # Cancel heartbeat task
        if "heartbeat_task" in locals():
            heartbeat_task.cancel()


@router.websocket("/ws/admin")
async def admin_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for admin panel real-time updates.
    Used for transaction status updates, booth changes, etc.
    """
    await websocket.accept()
    admin_connections.append(websocket)
    print(
        f"[WebSocket] Admin connected. Total admin connections: {len(admin_connections)}"
    )

    try:
        # Send initial connection confirmation
        await websocket.send_json(
            {
                "type": "connected",
                "role": "admin",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        while True:
            # Keep connection alive, wait for messages
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle ping/pong for connection keep-alive
                if message.get("type") == "ping":
                    await websocket.send_json(
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                    )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid JSON format"}
                )

    except WebSocketDisconnect:
        print("[WebSocket] Admin disconnected")
    except Exception as e:
        print(f"[WebSocket] Admin WebSocket error: {e}")
    finally:
        # Clean up
        if websocket in admin_connections:
            admin_connections.remove(websocket)
        print(
            f"[WebSocket] Admin removed. Total admin connections: {len(admin_connections)}"
        )


async def heartbeat_sender(websocket: WebSocket, device_id: str):
    """Send periodic heartbeat to client."""
    while True:
        try:
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            await websocket.send_json(
                {"type": "ping", "timestamp": datetime.utcnow().isoformat()}
            )
        except Exception:
            break


async def kick_device(device_id: str, reason: str = "Device kicked by admin"):
    """
    Kick a device from its session.
    Call this function from admin routes when a device needs to be disconnected.
    """
    if device_id in active_connections:
        websocket = active_connections[device_id]
        try:
            await websocket.send_json(
                {
                    "type": "kicked",
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            await websocket.close(code=4001, reason=reason)
        except Exception:
            pass
        finally:
            if device_id in active_connections:
                del active_connections[device_id]

    return True


async def notify_booth_update(booth_id: str, booth_data: dict):
    """
    Notify all devices assigned to a booth about booth updates.
    """
    # Find all devices assigned to this booth
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(DeviceSession).where(DeviceSession.booth_id == booth_id)
        )
        device_sessions = result.scalars().all()

        for device_session in device_sessions:
            if device_session.device_id in active_connections:
                websocket = active_connections[device_session.device_id]
                try:
                    await websocket.send_json(
                        {
                            "type": "booth_update",
                            "booth": booth_data,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                except Exception:
                    pass


async def broadcast_transaction_update(transaction_data: dict):
    """
    Broadcast transaction status update to all connected admin clients.
    Call this when a payment status changes (success, failed, etc.)
    """
    message = {
        "type": "transaction_update",
        "data": transaction_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    print(
        f"[WebSocket] Broadcasting transaction update to {len(admin_connections)} admin clients"
    )
    print(
        f"[WebSocket] Transaction: {transaction_data.get('id')} - Status: {transaction_data.get('status')}"
    )

    # Send to all connected admin clients
    disconnected = []
    for websocket in admin_connections:
        try:
            await websocket.send_json(message)
            print("[WebSocket] Sent to admin client")
        except Exception as e:
            print(f"[WebSocket] Error sending to admin client: {e}")
            disconnected.append(websocket)

    # Clean up disconnected clients
    for ws in disconnected:
        if ws in admin_connections:
            admin_connections.remove(ws)

    print(f"[WebSocket] Broadcast complete. {len(admin_connections)} clients remaining")
