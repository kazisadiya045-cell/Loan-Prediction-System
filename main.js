"use strict";
let lastResult = null, lastInputs = null;

// Education card picker
document.querySelectorAll(".edu-card").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".edu-card").forEach(b => b.classList.remove("selected"));
    btn.classList.add("selected");
    document.getElementById("education").value = btn.dataset.val;
  });
});

// Credit score live badge
function updateCreditDisplay(val) {
  const badge = document.getElementById("creditValue");
  badge.textContent = val;
  const v = parseInt(val);
  const color = v < 580 ? "#ff5a6e" : v < 670 ? "#f0a030" : v < 740 ? "#c9a84c" : v < 800 ? "#6acd7a" : "#22c97a";
  badge.style.color = badge.style.borderColor = color;
}
updateCreditDisplay(650);

// Live DTI meter
["income","loan_amount"].forEach(id => {
  document.getElementById(id)?.addEventListener("input", updateDTI);
});
function updateDTI() {
  const income = parseFloat(document.getElementById("income").value) || 0;
  const loan   = parseFloat(document.getElementById("loan_amount").value) || 0;
  const bar    = document.getElementById("dtiBar");
  const pct    = document.getElementById("dtiPct");
  if (!income || !loan) { bar.style.width="0"; pct.textContent="—"; return; }
  const ratio = Math.min((loan/income)*100, 100);
  bar.style.width = ratio + "%";
  pct.textContent = ratio.toFixed(1) + "%";
  const color = ratio < 30 ? "var(--green)" : ratio < 50 ? "var(--gold)" : "var(--red)";
  bar.style.background = pct.style.color = color;
}

// Step navigation
function goToStep(n) {
  if (n === 2 && !validateStep1()) return;
  document.querySelectorAll(".form-step").forEach(s => s.classList.remove("active"));
  document.getElementById("step"+n).classList.add("active");
  document.querySelectorAll(".step").forEach(s => {
    const sn = parseInt(s.dataset.step);
    s.classList.remove("active","done");
    if (sn === n) s.classList.add("active");
    if (sn < n)  { s.classList.add("done"); s.querySelector(".step-dot").textContent = "✓"; }
  });
}

// Validation
function markError(id, msg) {
  document.getElementById(id)?.classList.add("error");
  showToast("⚠ "+msg, "error"); return false;
}
function clearErrors() {
  document.querySelectorAll("input,select").forEach(el => el.classList.remove("error"));
}
function validateStep1() {
  clearErrors();
  const age = parseInt(document.getElementById("age").value);
  if (!age || age<18||age>100) return markError("age","Valid age required (18–100).");
  if (!document.getElementById("marital_status").value) return showToast("⚠ Select marital status","error"),false;
  if (!document.getElementById("education").value) return showToast("⚠ Select education level","error"),false;
  if (isNaN(parseInt(document.getElementById("employment_years").value))) return markError("employment_years","Enter employment years.");
  if (isNaN(parseInt(document.getElementById("existing_loans").value))) return markError("existing_loans","Enter existing loans.");
  return true;
}
function validateStep2() {
  clearErrors();
  if (!parseFloat(document.getElementById("income").value)) return markError("income","Enter your income.");
  if (!parseFloat(document.getElementById("loan_amount").value)) return markError("loan_amount","Enter loan amount.");
  return true;
}

// Predict
async function submitPrediction() {
  if (!validateStep2()) return;
  const payload = {
    age:              parseInt(document.getElementById("age").value),
    income:           parseFloat(document.getElementById("income").value),
    loan_amount:      parseFloat(document.getElementById("loan_amount").value),
    credit_score:     parseInt(document.getElementById("credit_score").value),
    employment_years: parseInt(document.getElementById("employment_years").value),
    existing_loans:   parseInt(document.getElementById("existing_loans").value),
    marital_status:   document.getElementById("marital_status").value,
    education:        document.getElementById("education").value,
  };
  lastInputs = payload;
  document.getElementById("btnLabel").textContent = "Analysing…";
  document.getElementById("spinner").classList.remove("hidden");
  try {
    const res  = await fetch("/predict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data = await res.json();
    if (!data.success) throw new Error(data.error||"Prediction failed.");
    lastResult = data;
    showResult(data, payload);
    goToStep(3);
    if (data.prediction === 1) launchConfetti();
  } catch(e) {
    showToast("❌ "+e.message,"error");
  } finally {
    document.getElementById("btnLabel").textContent = "Predict Now";
    document.getElementById("spinner").classList.add("hidden");
  }
}

// Render result
function showResult(data, inputs) {
  const approved = data.prediction === 1;
  const pa = (data.prob_approved*100).toFixed(1);
  const pr = (data.prob_rejected*100).toFixed(1);
  const dti = inputs.income ? ((inputs.loan_amount/inputs.income)*100).toFixed(1)+"%" : "N/A";
  document.getElementById("resultContainer").innerHTML = `
    <div class="result-badge ${approved?"approved":"rejected"}">${approved?"✅":"❌"} Loan ${approved?"Approved":"Rejected"}</div>
    <p class="result-message">${data.message}</p>
    <div class="prob-bars">
      <div class="prob-row"><span class="prob-label">Approved</span><div class="prob-track"><div class="prob-fill green" id="fillApprove"></div></div><span class="prob-pct" style="color:var(--green)">${pa}%</span></div>
      <div class="prob-row"><span class="prob-label">Rejected</span><div class="prob-track"><div class="prob-fill red"   id="fillReject"></div></div><span class="prob-pct" style="color:var(--red)">${pr}%</span></div>
    </div>
    <div class="detail-grid">
      <div class="detail-item"><div class="detail-key">Age</div><div class="detail-val">${inputs.age} yrs</div></div>
      <div class="detail-item"><div class="detail-key">Annual Income</div><div class="detail-val">₹${inputs.income.toLocaleString("en-IN")}</div></div>
      <div class="detail-item"><div class="detail-key">Loan Amount</div><div class="detail-val">₹${inputs.loan_amount.toLocaleString("en-IN")}</div></div>
      <div class="detail-item"><div class="detail-key">Credit Score</div><div class="detail-val">${inputs.credit_score}</div></div>
      <div class="detail-item"><div class="detail-key">Employment</div><div class="detail-val">${inputs.employment_years} yrs</div></div>
      <div class="detail-item"><div class="detail-key">Loan-to-Income</div><div class="detail-val">${dti}</div></div>
    </div>`;
  requestAnimationFrame(()=>setTimeout(()=>{
    document.getElementById("fillApprove").style.width = pa+"%";
    document.getElementById("fillReject").style.width  = pr+"%";
  },200));
}

// Save to DB
async function saveToDb() {
  if (!lastResult||!lastInputs) return;
  try {
    const res  = await fetch("/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({...lastInputs,...lastResult})});
    const data = await res.json();
    const msg  = document.getElementById("saveMsg");
    msg.classList.remove("hidden");
    if (data.success) { msg.textContent=`✅ Saved! Record ID: ${data.id}`; msg.style.color="var(--green)"; showToast("Saved ✅","success"); }
    else              { msg.textContent="⚠ "+(data.error||"DB unavailable."); msg.style.color="var(--red)"; }
  } catch(e) { showToast("❌ Could not reach server.","error"); }
}

// Reset
function resetForm() {
  ["age","income","loan_amount","employment_years","existing_loans"].forEach(id=>document.getElementById(id).value="");
  document.getElementById("marital_status").value="";
  document.getElementById("education").value="";
  document.getElementById("credit_score").value=650;
  document.querySelectorAll(".edu-card").forEach(b=>b.classList.remove("selected"));
  updateCreditDisplay(650); updateDTI(); clearErrors();
  document.getElementById("saveMsg").classList.add("hidden");
  lastResult=null; lastInputs=null;
  goToStep(1);
}

// Toast
function showToast(msg,type="success") {
  const t=document.getElementById("toast");
  t.textContent=msg; t.className="toast show "+type;
  setTimeout(()=>t.classList.remove("show"),3200);
}

// Confetti
function launchConfetti() {
  const canvas=document.getElementById("confettiCanvas"),ctx=canvas.getContext("2d");
  canvas.width=window.innerWidth; canvas.height=window.innerHeight;
  const COLORS=["#c9a84c","#f0d080","#22c97a","#00d4aa","#ff9f45","#fff"];
  const pieces=Array.from({length:180},()=>({
    x:Math.random()*canvas.width, y:Math.random()*-canvas.height,
    r:Math.random()*6+3, d:Math.random()*3+1.5,
    c:COLORS[Math.floor(Math.random()*COLORS.length)],
    tiltAngle:0, tiltSpeed:Math.random()*.1+.04,
    shape:Math.random()>.5?"circle":"rect"
  }));
  let ttl=220,frameId;
  function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    pieces.forEach(p=>{
      ctx.beginPath(); ctx.fillStyle=p.c; ctx.globalAlpha=ttl/220;
      if(p.shape==="circle"){ctx.arc(p.x,p.y,p.r,0,Math.PI*2);}
      else{ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.tiltAngle);ctx.fillRect(-p.r,-p.r*.5,p.r*2,p.r);ctx.restore();}
      ctx.fill();
      p.y+=p.d; p.tiltAngle+=p.tiltSpeed; p.x+=Math.sin(p.tiltAngle)*1.5;
      if(p.y>canvas.height){p.y=-10;p.x=Math.random()*canvas.width;}
    });
    if(--ttl>0) frameId=requestAnimationFrame(draw);
    else ctx.clearRect(0,0,canvas.width,canvas.height);
  }
  cancelAnimationFrame(frameId); draw();
}