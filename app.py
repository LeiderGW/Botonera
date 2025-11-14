import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import threading

import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Datos globales ---
COLORES = [
    "red", "blue", "green", "yellow", "purple",
    "orange", "pink", "cyan", "lime", "brown"
]

equipos = {}  # {websocket: color}
puntos = {c: 0 for c in COLORES}
turno_actual = None
admin_connections = []
lock = threading.Lock()

# ---------------------- VISTAS ----------------------

@app.get("/", response_class=HTMLResponse)
async def equipo(request: Request):
    return templates.TemplateResponse("equipo.html", {"request": request, "colores": COLORES})

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "puntos": puntos,
        "turno": turno_actual
    })

# ---------------- WEB SOCKETS ----------------

@app.websocket("/ws/equipo")
async def ws_equipo(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            action = data["action"]

            # --- Seleccionar color ---
            if action == "seleccionar_color":
                color = data["color"]
                if color in equipos.values():
                    await ws.send_json({"type": "color_ocupado", "color": color})
                else:
                    equipos[ws] = color
                    await ws.send_json({"type": "color_asignado", "color": color})

            # --- Pulsar botón ---
            elif action == "pulsar":
                global turno_actual
                with lock:
                    if turno_actual is None:
                        turno_actual = equipos.get(ws)
                        # Notificar a administradores
                        for admin in admin_connections:
                            await admin.send_json({"type": "turno_registrado", "color": turno_actual})

    except WebSocketDisconnect:
        if ws in equipos:
            del equipos[ws]


@app.websocket("/ws/admin")
async def ws_admin(ws: WebSocket):
    await ws.accept()
    admin_connections.append(ws)

    try:
        while True:
            data = await ws.receive_json()
            action = data["action"]

            # --- Reset turno ---
            if action == "reset_turno":
                global turno_actual
                turno_actual = None
                for admin in admin_connections:
                    await admin.send_json({"type": "turno_reseteado"})

            # --- Sumar puntos ---
            elif action == "sumar_puntos":
                color = data["color"]
                puntos[color] += 1

                # reenviar a todos los admin
                for admin in admin_connections:
                    await admin.send_json({"type": "puntos_actualizados", "puntos": puntos})

    except WebSocketDisconnect:
        admin_connections.remove(ws)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)