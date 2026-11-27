const SCALE = 2;
const TABLE_BOX = 130;
const SEAT_RADIUS = 52;

const floor = document.getElementById("floor");
floor.style.width = FLOOR_W * SCALE + "px";
floor.style.height = FLOOR_H * SCALE + "px";

// Stage, DJ, etc.
FEATURES.forEach(f => {
  const el = document.createElement("div");
  el.className = "feature";
  el.textContent = f.label;
  el.style.left = f.x * SCALE + "px";
  el.style.top = f.y * SCALE + "px";
  el.style.width = f.w * SCALE + "px";
  el.style.height = f.h * SCALE + "px";
  el.style.background = f.color;
  floor.appendChild(el);
});

// Tables and seats
TABLES.forEach(t => {
  const table = document.createElement("div");
  table.className = "table";
  table.style.left = t.x * SCALE - TABLE_BOX / 2 + "px";
  table.style.top = t.y * SCALE - TABLE_BOX / 2 + "px";

  const circle = document.createElement("div");
  circle.className = "table-circle";
  circle.textContent = t.number;
  table.appendChild(circle);

  for (let s = 1; s <= t.seats; s++) {
    const angle = (2 * Math.PI * (s - 1)) / t.seats - Math.PI / 2;
    const seat = document.createElement("div");
    seat.className = "seat";
    seat.dataset.id = `T${t.number}-S${s}`;
    seat.title = `Table ${t.number}, seat ${s}`;
    seat.style.left = `calc(50% + ${Math.cos(angle) * SEAT_RADIUS}px)`;
    seat.style.top = `calc(50% + ${Math.sin(angle) * SEAT_RADIUS}px)`;
    table.appendChild(seat);
  }

  floor.appendChild(table);
});

// ---- Selecting and saving ----
const countEl = document.getElementById("count");
const messageEl = document.getElementById("message");
const confirmBtn = document.getElementById("confirm");
const selected = new Set();
let taken = new Set(TAKEN);

function showMessage(text, ok = false) {
  messageEl.textContent = text;
  messageEl.style.color = ok ? "green" : "crimson";
}

// Paint taken seats red
function markTaken() {
  floor.querySelectorAll(".seat").forEach(seat => {
    seat.classList.toggle("taken", taken.has(seat.dataset.id));
  });
}

// Pre-select seats this user has already saved
SAVED.forEach(id => {
  const seat = floor.querySelector(`[data-id="${id}"]`);
  if (seat && !taken.has(id)) {
    selected.add(id);
    seat.classList.add("selected");
  }
});
markTaken();
countEl.textContent = selected.size;

floor.addEventListener("click", event => {
  const seat = event.target.closest(".seat");
  if (!seat) return;

  const id = seat.dataset.id;

  if (taken.has(id)) {
    showMessage("That seat is already taken.");
    return;
  }

  if (selected.has(id)) {
    selected.delete(id);
    seat.classList.remove("selected");
    showMessage("");
  } else if (selected.size < ALLOWED) {
    selected.add(id);
    seat.classList.add("selected");
    showMessage("");
  } else {
    showMessage(`You only have ${ALLOWED} ticket(s). Deselect a seat first.`);
  }

  countEl.textContent = selected.size;
});

confirmBtn.addEventListener("click", async () => {
  confirmBtn.disabled = true;
  try {
    const res = await fetch("/api/seats", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seats: [...selected] }),
    });
    const data = await res.json();

    if (res.status === 401 || res.status === 403) {
      location.href = "/";
    } else if (res.status === 409) {
      // Someone beat us to a seat: update the map and drop the lost seats
      taken = new Set(data.taken);
      selected.forEach(id => {
        if (taken.has(id)) {
          selected.delete(id);
          const seat = floor.querySelector(`[data-id="${id}"]`);
          if (seat) seat.classList.remove("selected");
        }
      });
      markTaken();
      countEl.textContent = selected.size;
      showMessage(data.error);
    } else if (res.ok) {
      showMessage("Seats saved!", true);
    } else {
      showMessage(data.error);
    }
  } catch (err) {
    showMessage("Couldn't reach the server. Please try again.");
  } finally {
    confirmBtn.disabled = false;
  }
});

// ---- Quiet refresh ----
async function refreshTaken() {
  if (document.hidden || confirmBtn.disabled) return; // skip background tabs and mid-save
  try {
    const res = await fetch("/api/taken");
    if (res.status === 401 || res.status === 403) {
      location.href = "/";
      return;
    }
    if (!res.ok) return;
    const data = await res.json();
    taken = new Set(data.taken);

    // If someone took a seat I had selected, drop it and tell me
    let lost = 0;
    selected.forEach(id => {
      if (taken.has(id)) {
        selected.delete(id);
        const seat = floor.querySelector(`[data-id="${id}"]`);
        if (seat) seat.classList.remove("selected");
        lost++;
      }
    });
    markTaken();
    countEl.textContent = selected.size;
    if (lost) showMessage("A seat you selected was just taken by someone else.");
  } catch (err) {
    // Ignore network blips; the next refresh will try again
  }
}

setInterval(refreshTaken, 10000);
