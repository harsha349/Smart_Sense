// document.getElementById("upload").onclick = async () => {
//   const f = document.getElementById("img").files[0];
//   if(!f) { alert("Choose image"); return; }
//   const diet = document.getElementById("diet").value;
//   const fd = new FormData();
//   fd.append("image", f);
//   if (diet) fd.append("diet", diet);

//   const res = await fetch("/api/analyze", { method: "POST", body: fd });
//   const data = await res.json();
//   document.getElementById("out").innerText = JSON.stringify(data, null, 2);
// };

// frontend/js/chat.js

const chatContainer = document.getElementById("chat-container");

const sendBtn = document.getElementById("send-btn");



function addMessage(html, sender="bot") {

  const msg = document.createElement("div");

  msg.className = "message " + sender;

  msg.innerHTML = html;

  chatContainer.appendChild(msg);

  chatContainer.scrollTop = chatContainer.scrollHeight;

}



function formatResponse(data) {

  let html = "";



  // Vision Items

  if(data.vision && data.vision.items.length > 0){

    html += `<div class="section"><b>Detected Items:</b>`;

    data.vision.items.forEach(i => {

      html += `<span class="badge">${i.name} (Conf: ${i.confidence})</span>`;

    });

    html += `</div>`;

  }



  // Nutrition

  if(data.nutrition && data.nutrition.totals_per_serving){

    const n = data.nutrition.totals_per_serving;

    html += `<div class="section"><b>Nutrition per serving:</b>`;

    html += `<div class="nutrition-card">`;

    html += `<div class="nutrient">Calories: ${n.cal}</div>`;

    html += `<div class="nutrient">Protein: ${n.protein}</div>`;

    html += `<div class="nutrient">Carbs: ${n.carbs}</div>`;

    html += `<div class="nutrient">Fat: ${n.fat}</div>`;

    html += `<div class="nutrient">Fiber: ${n.fiber}</div>`;

    html += `</div></div>`;

  }



  // Health

  if(data.health && data.health.length > 0){

    html += `<div class="section"><b>Health Summary:</b>`;

    data.health.forEach(h => {

      html += `<span class="badge">${h.health_summary} (Score: ${h.score})</span>`;

    });

    html += `</div>`;

  }



  // Recipes

  if(data.recipes && data.recipes.recipes.length > 0){

    html += `<div class="section"><b>Recipes:</b>`;

    data.recipes.recipes.forEach(r => {

      html += `<div class="recipe-card"><b>${r.title}</b> (${r.difficulty})<br>`;

      html += `Ingredients: ${r.ingredients.map(i=>i.name+" "+i.qty).join(", ")}<br>`;

      html += `Steps: ${r.steps.join(", ")}<br>`;

      html += `Time: ${r.time}</div>`;

    });

    html += `</div>`;

  }



  return html;

}



sendBtn.onclick = async () => {

  const fileInput = document.getElementById("img");

  const dietInput = document.getElementById("diet");

  const file = fileInput.files[0];

  const diet = dietInput.value;



  if(!file){

    alert("Please choose an image");

    return;

  }



  addMessage(`<b>You:</b> Uploaded image (${file.name})`, "user");



  const fd = new FormData();

  fd.append("image", file);

  if(diet) fd.append("diet", diet);



  addMessage("<i>Bot is processing...</i>", "bot");



  try {

    const res = await fetch("/api/analyze", { method: "POST", body: fd });

    const data = await res.json();

    chatContainer.lastChild.remove(); // remove "processing" message

    addMessage(formatResponse(data), "bot");

  } catch(e){

    chatContainer.lastChild.remove();

    addMessage("Error fetching API", "bot");

    console.error(e);

  }



  fileInput.value = "";

};