/*
============================================
© 2026 Akhil Reddy
GitHub: https://github.com/akhilmatta89
LinkedIn: https://www.linkedin.com/in/akhil-reddy-1a0822255
============================================
*/

import { auth, provider } from "./firebase-config.js";

import {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signInWithPopup,
    sendPasswordResetEmail
} from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";

/* === Elements === */
const signInWithGoogleButtonEl = document.getElementById("sign-in-with-google-btn")
const signUpWithGoogleButtonEl = document.getElementById("sign-up-with-google-btn")
const emailInputEl = document.getElementById("email-input")
const passwordInputEl = document.getElementById("password-input")
const signInButtonEl = document.getElementById("sign-in-btn")
const createAccountButtonEl = document.getElementById("create-account-btn")

const errorMsgEmail = document.getElementById("email-error-message")
const errorMsgPassword = document.getElementById("password-error-message")
const errorMsgGoogleSignIn = document.getElementById("google-signin-error-message")

const resetPasswordView = document.getElementById("reset-password-view")

document.addEventListener("DOMContentLoaded", () => {

    const forgotPasswordLink = document.getElementById("forgot-password-link");
    const backToLogin = document.getElementById("back-to-login");
    const loginView = document.getElementById("login-view");
    const resetView = document.getElementById("reset-view");
    const forgotPasswordButton = document.getElementById("forgot-password-btn");

    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener("click", (e) => {
            e.preventDefault();
            console.log("Forgot clicked");

            loginView.style.display = "none";
            resetView.style.display = "block";
        });
    }

    if (backToLogin) {
        backToLogin.addEventListener("click", (e) => {
            e.preventDefault();
            resetView.style.display = "none";
            loginView.style.display = "block";
        });
    }

    // 🔥 THIS WAS MISSING
    if (forgotPasswordButton) {
        forgotPasswordButton.addEventListener("click", resetPassword);
    }

});

/* === Event Listeners === */
if (signInWithGoogleButtonEl) {
    signInWithGoogleButtonEl.addEventListener("click", authSignInWithGoogle)
}

if (signInButtonEl) {
    signInButtonEl.addEventListener("click", authSignInWithEmail)
}

if (createAccountButtonEl) {
    createAccountButtonEl.addEventListener("click", authCreateAccountWithEmail)
}

if (signUpWithGoogleButtonEl) {
    signUpWithGoogleButtonEl.addEventListener("click", authSignUpWithGoogle)
}

/* === Google Sign-In === */
async function authSignInWithGoogle() {
    try {
        const result = await signInWithPopup(auth, provider)
        const user = result.user
        const idToken = await user.getIdToken()
        loginUser(idToken)

    } catch (error) {
        console.error("Google Sign-In Error:", error)
        if (errorMsgGoogleSignIn) {
            errorMsgGoogleSignIn.textContent = error.message
        }
    }
}

/* === Google Sign-Up === */
async function authSignUpWithGoogle() {
    try {
        const result = await signInWithPopup(auth, provider)
        const user = result.user
        const idToken = await user.getIdToken()
        loginUser(idToken)

    } catch (error) {
        console.error("Google Signup Error:", error)
    }
}

/* === Email Sign-In === */
function authSignInWithEmail() {
    const email = emailInputEl.value
    const password = passwordInputEl.value

    signInWithEmailAndPassword(auth, email, password)
        .then(async (userCredential) => {
            const idToken = await userCredential.user.getIdToken()
            loginUser(idToken)
        })
        .catch((error) => {
            console.error(error)
            errorMsgPassword.textContent = "Invalid email or password"
        })
}

/* === Email Sign-Up === */
function authCreateAccountWithEmail() {
    const email = emailInputEl.value
    const password = passwordInputEl.value

    createUserWithEmailAndPassword(auth, email, password)
        .then(async (userCredential) => {
            const idToken = await userCredential.user.getIdToken()
            loginUser(idToken)
        })
        .catch((error) => {
            console.error(error)
            errorMsgEmail.textContent = error.message
        })
}

/* === Send token to Flask === */
function loginUser(idToken) {
    fetch('/auth', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${idToken}`
        }
    }).then(res => {
        if (res.ok) {
            window.location.href = "/dashboard"
        } else {
            console.error("Login failed")
        }
    })
}

function resetPassword() {
    const emailToReset = document.getElementById("email-forgot-password").value;

    if (!emailToReset) {
        alert("Please enter your email");
        return;
    }

    sendPasswordResetEmail(auth, emailToReset, {
        url: window.location.origin + "/login"
    })
    .then(() => {
        alert("Reset email sent ✅");

        // 🔥 FIX: re-fetch elements here
        const loginView = document.getElementById("login-view");
        const resetView = document.getElementById("reset-view");

        resetView.style.display = "none";
        loginView.style.display = "block";

        // Optional: auto-fill email
        document.getElementById("email-input").value = emailToReset;
    })
    .catch((error) => {
        console.error(error);
        alert(error.message);
    });
}