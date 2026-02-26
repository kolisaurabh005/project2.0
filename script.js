async function resetPassword() {
  const emailOrPhone = document.getElementById("emailOrPhone").value;
  const message = document.getElementById("message");
  const newPass = document.getElementById("newPass");
  const button = document.getElementById("resetBtn");
  const spinner = document.getElementById("spinner");
  const btnText = document.getElementById("btnText");

  message.innerText = "";
  newPass.innerText = "";
  newPass.classList.remove("show");

  if (!emailOrPhone) {
    message.innerText = "Please enter email or phone";
    return;
  }

  button.disabled = true;
  spinner.style.display = "inline-block";
  btnText.style.opacity = "0.5";

  const response = await fetch("/forgot-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emailOrPhone })
  });

  const data = await response.json();

  spinner.style.display = "none";
  btnText.style.opacity = "1";
  button.disabled = false;

  if (!data.success) {
    message.innerText = data.message;
  } else {
    message.innerText = data.message;
    newPass.innerText = "New Password: " + data.newPassword;
    newPass.classList.add("show");
  }
}

/* Dark Mode Toggle */
document.getElementById("darkToggle").addEventListener("change", function () {
  document.body.classList.toggle("dark");
});
