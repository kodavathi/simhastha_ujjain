// ==== CONFIG (replace with your EmailJS values) ====
const EMAILJS_SERVICE_ID = "service_mkg5zdi";
const EMAILJS_TEMPLATE_ID = "template_8ef4he4";
const EMAILJS_USER_ID = "6jJix5xHhmgxlPHX3";

// ==== DATA ====
let volunteers = []; // {name,email,lat,lon,assigned:false}
let assignedVolunteers = [];
let currentVictim = null;

// Add new volunteer (no duplicates)
function addVolunteer(name, email, lat, lon) {
  if (!name || !email || !lat || !lon) {
    alert("Please enter all details (name, email, latitude, longitude).");
    return;
  }
  if (volunteers.some(v => v.email === email)) {
    alert("Volunteer already exists!");
    return;
  }

  volunteers.push({ 
    name, 
    email, 
    lat: parseFloat(lat), 
    lon: parseFloat(lon), 
    assigned: false 
  });
  renderVolunteers();

  document.getElementById("name").value = "";
  document.getElementById("email").value = "";
  document.getElementById("lat").value = "";
  document.getElementById("lon").value = "";
}

// Render volunteers list
function renderVolunteers() {
  const list = document.getElementById("volunteer-list");
  list.innerHTML = "";

  volunteers.forEach((v, index) => {
    const item = document.createElement("div");
    item.className = "volunteer-item";

    if (v.assigned) {
      item.innerHTML = `
        <span>${v.name} (${v.email})</span>
        <span class="assigned">✅ Assigned</span>
        <button onclick="finishRescue('${v.email}')">Finish</button>
      `;
    } else {
      item.innerHTML = `
        <span>${v.name} (${v.email})</span>
        <button onclick="assignVolunteer(${index})">Assign</button>
      `;
    }
    list.appendChild(item);
  });
}

// Show victim alert
function showVictimAlert(message, lat, lon) {
  currentVictim = { message, lat, lon };

  document.getElementById("victimMessage").innerText = message;
  document.getElementById("victimLocation").innerText = `Lat: ${lat}, Lon: ${lon}`;
  document.getElementById("mapLink").href = `https://www.google.com/maps?q=${lat},${lon}`;
  document.getElementById("mapLink").style.display = "inline-block";

  document.getElementById("forwardBtn").disabled = false;

  logStatus("🚨 New victim alert received.");
}

// Assign volunteer manually
function assignVolunteer(index) {
  const volunteer = volunteers[index];
  if (!currentVictim) return alert("⚠️ No victim alert available!");
  if (volunteer.assigned) return alert(`${volunteer.name} already assigned!`);

  volunteer.assigned = true;
  assignedVolunteers.push(volunteer);
  sendEmail(volunteer, currentVictim.message, currentVictim.lat, currentVictim.lon);

  renderVolunteers();
  logStatus(`📤 Assigned ${volunteer.name}`);
}

// Auto-assign nearest volunteers
document.getElementById("forwardBtn").addEventListener("click", () => {
  if (!currentVictim) return;

  const available = volunteers.filter(v => !v.assigned);
  available.sort((a, b) => getDistance(a, currentVictim) - getDistance(b, currentVictim));

  if (available.length === 0) {
    logStatus("⚠️ No available volunteers!");
    return;
  }

  // pick top 3 nearest
  const nearest = available.slice(0, 3);
  nearest.forEach(v => assignVolunteer(volunteers.indexOf(v)));
});

// Haversine formula for distance (km)
function getDistance(v, victim) {
  const R = 6371;
  const dLat = toRad(victim.lat - v.lat);
  const dLon = toRad(victim.lon - v.lon);
  const lat1 = toRad(v.lat);
  const lat2 = toRad(victim.lat);

  const a = Math.sin(dLat/2)**2 + Math.sin(dLon/2)**2 * Math.cos(lat1) * Math.cos(lat2);
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}
function toRad(v) { return v * Math.PI / 180; }

// Finish rescue
function finishRescue(email) {
  const v = volunteers.find(vol => vol.email === email);
  if (v) {
    v.assigned = false;
    assignedVolunteers = assignedVolunteers.filter(vol => vol.email !== email);
    renderVolunteers();
    logStatus(`✅ ${v.name} finished rescue.`);

    // Optional: clear victim SOS after finishing
    localStorage.removeItem("victimLocation");
    currentVictim = null;
    document.getElementById("victimMessage").innerText = "⚠️ No SOS received yet.";
    document.getElementById("victimLocation").innerText = "";
    document.getElementById("mapLink").style.display = "none";
    document.getElementById("forwardBtn").disabled = true;
  }
}

// Send email
function sendEmail(volunteer, message, lat, lon) {
  const locationLink = `https://www.google.com/maps?q=${lat},${lon}`;
  const params = {
    to_name: volunteer.name,
    to_email: volunteer.email,
    message,
    location_link: locationLink,
    from_name: "Admin SOS Dashboard"
  };

  emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, params, EMAILJS_USER_ID)
    .then(() => logStatus(`📩 Email sent to ${volunteer.name}`))
    .catch(err => logStatus(`❌ Email failed to ${volunteer.name}`));
}

// Status log with auto-remove
function logStatus(text) {
  const log = document.getElementById("statusLog");
  const entry = document.createElement("p");
  entry.innerText = text;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;

  setTimeout(() => {
    entry.remove();
  }, 5000);
}

// === Listen for Victim SOS ===
window.onload = function () {
  checkVictimLocation(); 
  setInterval(checkVictimLocation, 3000); // keep checking every 3 sec
};

function checkVictimLocation() {
  let locationData = localStorage.getItem("victimLocation");
  if (locationData) {
    let { lat, lon } = JSON.parse(locationData);
    showVictimAlert("🚨 SOS! Immediate help needed!", lat, lon);
  } else {
    document.getElementById("victimMessage").innerText = "⚠️ No SOS received yet.";
    document.getElementById("victimLocation").innerText = "";
    document.getElementById("mapLink").style.display = "none";
    document.getElementById("forwardBtn").disabled = true;
  }
}
