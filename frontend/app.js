document.getElementById("upload").onclick = async () => {
  const f = document.getElementById("img").files[0];
  if(!f) { alert("Choose image"); return; }
  const diet = document.getElementById("diet").value;
  const fd = new FormData();
  fd.append("image", f);
  if (diet) fd.append("diet", diet);

  const res = await fetch("/api/analyze", { method: "POST", body: fd });
  const data = await res.json();
  document.getElementById("out").innerText = JSON.stringify(data, null, 2);
};
