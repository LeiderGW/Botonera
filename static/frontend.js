// Detecta automáticamente si debe usar ws:// (local) o wss:// (Railway)
let protocol = location.protocol === "https:" ? "wss://" : "ws://";

// Usa el protocolo dinámico
let ws = new WebSocket(protocol + location.host + "/ws/equipo");

let miColor = null;


function seleccionarColor() {
    const color = document.getElementById("colorSelect").value;
    ws.send(JSON.stringify({ action: "seleccionar_color", color }));
}

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === "color_ocupado") {
        alert("Ese color ya está tomado!");
    }

    if (msg.type === "color_asignado") {
        miColor = msg.color;
        document.getElementById("colorElegido").innerText = "Tu color: " + miColor;
        let btn = document.getElementById("btnPulsar");
        btn.style.background = miColor;
        btn.disabled = false;
    }
};

function pulsar() {
    ws.send(JSON.stringify({ action: "pulsar" }));
}
