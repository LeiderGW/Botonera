
const wsProtocol = location.protocol === "https//";
const wsHost = location.host;

ws = new WebSocket(wsProtocol + wsHost + "/ws/equipo");

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
