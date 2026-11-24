function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast(`آی‌پی ${text} با موفقیت کپی شد! وارد بازی شوید.`);
  }).catch(() => {
    showToast(`آی‌پی: ${text}`);
  });
}

function showToast(message, icon = "✅") {
  const toast = document.getElementById("toast");
  const msgEl = document.getElementById("toast-message");
  const iconEl = document.getElementById("toast-icon");
  if (!toast) return;

  msgEl.innerText = message;
  iconEl.innerText = icon;
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3500);
}

function openRegisterModal(eventId, eventTitle) {
  document.getElementById("modal-event-id").value = eventId;
  document.getElementById("modal-event-title").innerText = eventTitle;
  document.getElementById("modal-error").classList.add("hidden");
  document.getElementById("modal-success").classList.add("hidden");
  document.getElementById("register-form").reset();
  document.getElementById("modal-event-id").value = eventId;
  document.getElementById("register-modal").classList.remove("hidden");
}

function closeRegisterModal() {
  document.getElementById("register-modal").classList.add("hidden");
}

async function handleRegister(event) {
  event.preventDefault();
  const eventId = document.getElementById("modal-event-id").value;
  const name = document.getElementById("reg-name").value.trim();
  const gamertag = document.getElementById("reg-gamertag").value.trim();
  const discord = document.getElementById("reg-discord").value.trim();
  const phone = document.getElementById("reg-phone").value.trim();
  const btn = document.getElementById("modal-submit-btn");
  const errBox = document.getElementById("modal-error");
  const succBox = document.getElementById("modal-success");

  errBox.classList.add("hidden");
  succBox.classList.add("hidden");
  btn.disabled = true;
  btn.innerText = "در حال ثبت اطلاعات...";

  try {
    const res = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        event_id: eventId,
        player_name: name,
        gamertag: gamertag,
        discord: discord,
        phone: phone
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "خطا در ثبت نام.");
    }

    succBox.innerText = data.message || "ثبت‌نام با موفقیت انجام شد!";
    succBox.classList.remove("hidden");
    btn.innerText = "ثبت شد ✓";

    setTimeout(() => {
      closeRegisterModal();
      window.location.reload();
    }, 2000);

  } catch (err) {
    errBox.innerText = err.message;
    errBox.classList.remove("hidden");
    btn.disabled = false;
    btn.innerText = "تلاش مجدد ثبت‌نام";
  }
}

async function refreshServers() {
  const icon = document.getElementById("refresh-icon");
  if (icon) icon.classList.add("animate-spin");

  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    if (data.total_players !== undefined) {
      const pEl = document.getElementById("stat-players");
      if (pEl) pEl.innerText = `${data.total_players}+`;
    }
    showToast("وضعیت سرورها با موفقیت به‌روزرسانی شد.");
  } catch (e) {
    showToast("خطا در برقراری ارتباط با سرور", "⚠️");
  } finally {
    if (icon) icon.classList.remove("animate-spin");
  }
}
