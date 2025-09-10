// ==== Initialize EmailJS ====
(function(){
    emailjs.init("6jJix5xHhmgxlPHX3"); // your Public Key
})();

// ==== SOS Button handler ====
document.getElementById("sosBtn").addEventListener("click", function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            let lat = position.coords.latitude;
            let lon = position.coords.longitude;
            let mapLink = `https://www.google.com/maps?q=${lat},${lon}`;

            // Save to localStorage (for Admin dashboard)
            localStorage.setItem("victimLocation", JSON.stringify({ lat, lon }));

            // Send email with location
            emailjs.send("service_mkg5zdi", "template_ren3mld", {
                from_name: "Rupesh",
                message: `🚨 SOS! Immediate help needed!\nMy Location: ${mapLink}`
            })
            .then(() => {
                document.getElementById("status").innerText = "✅ SOS Alert Sent with Location!";
            }, (err) => {
                document.getElementById("status").innerText = "❌ Failed: " + JSON.stringify(err);
            });

        }, function(error) {
            document.getElementById("status").innerText = "❌ Location access denied!";
        });
    } else {
        document.getElementById("status").innerText = "❌ Geolocation not supported.";
    }
});
