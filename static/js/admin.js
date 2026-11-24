function getAdminKey() {
  const el = document.getElementById("admin-key-input");
  return el ? el.value.trim() : "patogh2026";
}

async function updateBroadcast() {
  const message = document.getElementById("broadcast-input").value.trim();
  try {
    const res = await fetch("/api/admin/broadcast", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Key": getAdminKey()
      },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "خطا در ثبت پیام");
    alert("پیام اعلان با موفقیت به‌روزرسانی شد.");
  } catch (err) {
    alert(err.message);
  }
}

async function saveServer(id, status, max_players) {
  const pInput = document.getElementById(`srv-p-${id}`);
  const pingInput = document.getElementById(`srv-ping-${id}`);
  const players = pInput ? parseInt(pInput.value) : 0;
  const ping = pingInput ? pingInput.value : "20ms";

  try {
    const res = await fetch("/api/admin/servers", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Key": getAdminKey()
      },
      body: JSON.stringify({
        id,
        status,
        players,
        max_players,
        ping
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "خطا در تغییر وضعیت سرور");
    window.location.reload();
  } catch (err) {
    alert(err.message);
  }
}

async function handleCreateEvent(event) {
  event.preventDefault();
  const title = document.getElementById("ev-title").value.trim();
  const game = document.getElementById("ev-game").value.trim();
  const date = document.getElementById("ev-date").value.trim();
  const prize = document.getElementById("ev-prize").value.trim();
  const capacity = parseInt(document.getElementById("ev-capacity").value) || 32;
  const description = document.getElementById("ev-desc").value.trim();

  try {
    const res = await fetch("/api/admin/events", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Key": getAdminKey()
      },
      body: JSON.stringify({
        title,
        game,
        date,
        prize,
        capacity,
        description
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "خطا در ساخت رویداد");
    alert("رویداد جدید با موفقیت ایجاد شد!");
    window.location.reload();
  } catch (err) {
    alert(err.message);
  }
}

async function deleteEvent(eventId) {
  if (!confirm("آیا از حذف این رویداد مطمئن هستید؟")) return;

  try {
    const res = await fetch(`/api/admin/events/${eventId}`, {
      method: "DELETE",
      headers: {
        "X-Admin-Key": getAdminKey()
      }
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "خطا در حذف رویداد");
    window.location.reload();
  } catch (err) {
    alert(err.message);
  }
}
