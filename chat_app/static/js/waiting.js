async function checkVerification() {
    try{
        const response = await fetch("/verification_status", { cache: "no-store" })
        if(response.ok) {
            const data = await response.json()
            if(data.verified) {
                window.location.href = "/waiting";
            }
            else{
                setTimeout(checkVerification, 3000);
            }
        }
        else if (response.status === 401 || response.status === 404) {
            window.location.href = "/waiting";
        }
        else{
            setTimeout(checkVerification, 3000);
        }
    }
    catch(error){
        console.error(error);
        setTimeout(checkVerification, 3000);
    }
}

const resendButton = document.getElementById("resend-button");
let remainingSeconds = Number(resendButton.dataset.remaining);
const resendError = document.getElementById("resend-error");

function updateTimer() {
    
    if (remainingSeconds > 0) {
        resendButton.disabled = true
        resendButton.textContent = `Надіслати лист повторно (${remainingSeconds} с)`;
        remainingSeconds--;
        setTimeout(updateTimer, 1000);
    }
    else {
        resendButton.disabled = false
        resendButton.textContent = "Надіслати лист повторно";
    }
}
updateTimer();

async function resendVerification() {
    resendButton.disabled = true;
    resendButton.textContent = "Надсилання...";
    resendError.hidden = true;

    try {
        const response = await fetch("/resend_verification", {
            method: "POST"
        });

        if (response.ok) {
            remainingSeconds = 60;
            updateTimer();
            return;
        }

        if (response.status === 429) {
            const data = await response.json();
            remainingSeconds = data.remaining_seconds;
            updateTimer();
            return;
        }

        if ([401, 404, 409].includes(response.status)) {
            window.location.href = "/waiting";
            return;
        }

        throw new Error("Failed to send email");
    }
    catch (error) {
        resendError.textContent = "Не вдалося надіслати лист. Спробуйте ще раз.";
        resendError.hidden = false;
        resendButton.disabled = false;
        resendButton.textContent = "Надіслати лист повторно";
    }
}
checkVerification()

resendButton.addEventListener("click", resendVerification);