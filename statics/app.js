async function upload() {
    const fileInput = document.getElementById("file");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();
    document.getElementById("output").innerHTML = "Columns: " + data.columns.join(", ");
}

async function run() {
    const command = document.getElementById("command").value;
    document.getElementById("loading").style.display = "block";

    const res = await fetch("/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
    });

    const data = await res.json();
    document.getElementById("loading").style.display = "none";

    let html = "";
    if (data.error) {
        html = "<p style='color:red'>" + data.error + "</p>";
    } else {
        html = data.result;
        if (data.plot) {
            html += `<img src="${data.plot}" style="max-width:100%">`;
        }
        if (data.explanation) {
            html += `<