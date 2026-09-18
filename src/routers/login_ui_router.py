# pylint: disable=too-many-lines
"""
Browser login UI served by FastAPI.

Provides:
    - Employee login
    - Forgot Password flow
    - Employee creation for authenticated managers
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>CodeBusters Login</title>

    <style>
        * {
            box-sizing: border-box;
        }

        html,
        body {
            margin: 0;
            padding: 0;
            width: 100%;
            min-height: 100%;
            overflow-x: hidden;
        }

        html {
            background: #020803;
        }

        body {
            min-height: 100dvh;
            color: #d9ffd0;
            font-family: "Courier New", Courier, monospace;
            background:
                radial-gradient(
                    circle at center,
                    rgba(20, 60, 20, 0.18) 0%,
                    rgba(0, 0, 0, 0.98) 70%
                ),
                #020803;
        }

        /* =========================================================
           PAGE LAYOUT
           ========================================================= */

        .page {
            min-height: 100dvh;
            width: 100%;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /*
         * THIS is the important part.
         *
         * The page content can grow taller than the browser.
         * The content area scrolls vertically while the footer
         * remains visible at the bottom.
         */
        .page-scroll {
            flex: 1 1 auto;
            min-height: 0;
            width: 100%;
            overflow-x: hidden;
            overflow-y: auto;
            scroll-behavior: smooth;

            padding: 24px 20px 40px;
        }

        .page-scroll::-webkit-scrollbar {
            width: 10px;
        }

        .page-scroll::-webkit-scrollbar-track {
            background: #020803;
        }

        .page-scroll::-webkit-scrollbar-thumb {
            background: #39ff14;
            border-radius: 6px;
            box-shadow:
                0 0 8px rgba(57, 255, 20, 0.75);
        }

        .main-content {
            min-height: 100%;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }

        /* =========================================================
           BACKGROUND
           ========================================================= */

        .matrix-background {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;

            opacity: 0.10;

            background-image:
                linear-gradient(
                    rgba(57, 255, 20, 0.05) 1px,
                    transparent 1px
                ),
                linear-gradient(
                    90deg,
                    rgba(57, 255, 20, 0.05) 1px,
                    transparent 1px
                );

            background-size: 22px 22px;
        }

        .matrix-background::before {
            content: "";
            position: absolute;
            inset: 0;

            background:
                repeating-linear-gradient(
                    180deg,
                    rgba(57, 255, 20, 0.08) 0px,
                    rgba(57, 255, 20, 0.08) 1px,
                    transparent 1px,
                    transparent 6px
                );

            animation: scan 8s linear infinite;
        }

        @keyframes scan {
            from {
                transform: translateY(-20px);
            }

            to {
                transform: translateY(20px);
            }
        }

        /* =========================================================
           CARD
           ========================================================= */

        .card {
            position: relative;
            z-index: 2;

            width: min(560px, 100%);
            max-width: 560px;

            margin: 12px auto 24px;

            padding: 30px;

            background:
                linear-gradient(
                    180deg,
                    rgba(2, 13, 5, 0.98),
                    rgba(0, 5, 2, 0.98)
                );

            border: 1px solid #39ff14;
            border-radius: 8px;

            box-shadow:
                0 0 12px rgba(57, 255, 20, 0.35),
                0 0 35px rgba(57, 255, 20, 0.12);

            overflow: visible;
        }

        /* =========================================================
           BRAND
           ========================================================= */

        .brand {
            text-align: center;
            margin-bottom: 24px;
        }

        .brand-symbol {
            font-size: 40px;
            color: #9dff39;

            text-shadow:
                0 0 8px #39ff14,
                0 0 18px #39ff14;
        }

        .brand-title {
            margin-top: 4px;

            font-size: 32px;
            font-weight: bold;
            letter-spacing: 5px;

            color: #9dff39;

            text-shadow:
                0 0 6px #39ff14,
                0 0 14px #39ff14,
                0 0 30px rgba(57, 255, 20, 0.65);
        }

        .brand-subtitle {
            margin-top: 6px;

            font-size: 12px;
            letter-spacing: 3px;

            color: #76ff4f;

            text-transform: uppercase;
        }

        /* =========================================================
           SCREEN SECTIONS
           ========================================================= */

        .screen {
            display: none;
        }

        .screen.active {
            display: block;
        }

        .screen-title {
            margin: 0 0 20px;

            font-size: 20px;
            color: #9dff39;

            text-align: center;

            text-shadow:
                0 0 7px #39ff14;
        }

        .screen-description {
            margin-bottom: 22px;

            color: #8fbf86;
            font-size: 12px;
            line-height: 1.7;
            text-align: center;
        }

        /* =========================================================
           FORM
           ========================================================= */

        .form-group {
            margin-bottom: 18px;
        }

        label {
            display: block;

            margin-bottom: 7px;

            font-size: 11px;
            letter-spacing: 1px;

            color: #75ff49;
            text-transform: uppercase;
        }

        input,
        select {
            width: 100%;

            min-height: 44px;

            padding: 11px 12px;

            color: #d9ffd0;
            background: rgba(0, 15, 4, 0.95);

            border: 1px solid #2caf18;
            border-radius: 4px;

            outline: none;

            font-family: "Courier New", Courier, monospace;
            font-size: 14px;

            transition:
                border-color 0.2s ease,
                box-shadow 0.2s ease;
        }

        input:focus,
        select:focus {
            border-color: #9dff39;

            box-shadow:
                0 0 7px rgba(57, 255, 20, 0.65),
                inset 0 0 7px rgba(57, 255, 20, 0.08);
        }

        input::placeholder {
            color: #56824f;
        }

        select {
            cursor: pointer;
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }

        /* =========================================================
           BUTTONS
           ========================================================= */

        button {
            font-family: "Courier New", Courier, monospace;
        }

        .primary-button {
            width: 100%;

            min-height: 46px;

            border: 1px solid #9dff39;
            border-radius: 4px;

            background: #123b08;
            color: #caffb7;

            cursor: pointer;

            font-size: 14px;
            font-weight: bold;
            letter-spacing: 2px;
            text-transform: uppercase;

            box-shadow:
                0 0 8px rgba(57, 255, 20, 0.45),
                inset 0 0 10px rgba(57, 255, 20, 0.08);

            transition:
                background 0.2s ease,
                box-shadow 0.2s ease,
                transform 0.15s ease;
        }

        .primary-button:hover {
            background: #1c5c0d;

            box-shadow:
                0 0 12px rgba(57, 255, 20, 0.75),
                0 0 25px rgba(57, 255, 20, 0.20);

            transform: translateY(-1px);
        }

        .primary-button:active {
            transform: translateY(0);
        }

        .account-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;

            gap: 18px;

            margin-top: 18px;
        }

        .secondary-link {
            flex: 1;

            border: none;
            background: transparent;

            color: #9dff39;

            font-size: 12px;

            cursor: pointer;

            padding: 6px;

            text-shadow:
                0 0 5px #39ff14;

            transition:
                color 0.2s ease,
                text-shadow 0.2s ease;
        }

        .secondary-link:hover {
            color: #d7ffbe;

            text-shadow:
                0 0 8px #39ff14,
                0 0 15px #39ff14;
        }

        .back-button {
            width: 100%;

            border: 1px solid #245c1b;
            background: transparent;

            color: #7fd66a;

            min-height: 40px;

            border-radius: 4px;

            cursor: pointer;

            margin-top: 14px;
        }

        .back-button:hover {
            border-color: #39ff14;
            color: #baff9f;
        }

        /* =========================================================
           MESSAGES
           ========================================================= */

        .message {
            display: none;

            margin-top: 16px;
            padding: 12px;

            border-radius: 4px;

            font-size: 12px;
            line-height: 1.6;
        }

        .message.visible {
            display: block;
        }

        .message.success {
            color: #baff9f;

            border: 1px solid #39ff14;

            background: rgba(20, 80, 10, 0.20);

            box-shadow:
                0 0 10px rgba(57, 255, 20, 0.20);
        }

        .message.error {
            color: #ff8f8f;

            border: 1px solid #ff4141;

            background: rgba(90, 0, 0, 0.20);

            box-shadow:
                0 0 10px rgba(255, 65, 65, 0.18);
        }

        /* =========================================================
           FOOTER
           ========================================================= */

        .footer {
            position: sticky;
            bottom: 0;

            z-index: 100;

            flex: 0 0 auto;

            width: 100%;

            padding: 10px 20px;

            text-align: center;

            background:
                linear-gradient(
                    180deg,
                    rgba(0, 8, 2, 0.88),
                    rgba(0, 2, 1, 0.98)
                );

            border-top: 1px solid rgba(57, 255, 20, 0.45);

            box-shadow:
                0 -4px 16px rgba(57, 255, 20, 0.08);

            backdrop-filter: blur(8px);
        }

        .footer-title {
            color: #9dff39;

            font-size: 11px;
            letter-spacing: 3px;

            text-shadow:
                0 0 6px #39ff14;
        }

        .footer-subtitle {
            margin-top: 3px;

            color: #56824f;

            font-size: 9px;
            letter-spacing: 1px;
        }

        /* =========================================================
           MOBILE
           ========================================================= */

        @media (max-width: 700px) {
            .page-scroll {
                padding: 16px 12px 28px;
            }

            .card {
                padding: 22px 18px;

                margin-top: 5px;
                margin-bottom: 20px;
            }

            .brand-title {
                font-size: 27px;
                letter-spacing: 4px;
            }

            .brand-symbol {
                font-size: 34px;
            }

            .form-grid {
                grid-template-columns: 1fr;
                gap: 0;
            }
        }

        @media (max-width: 480px) {
            .account-actions {
                flex-direction: row;
                gap: 8px;
            }

            .secondary-link {
                font-size: 10px;
                padding-left: 2px;
                padding-right: 2px;
            }

            .footer {
                padding-left: 10px;
                padding-right: 10px;
            }
        }
    </style>
</head>

<body>

<div class="matrix-background"></div>

<div class="page">

    <!-- =========================================================
         SCROLLABLE CONTENT
         ========================================================= -->

    <div class="page-scroll">

        <main class="main-content">

            <section class="card">

                <!-- =================================================
                     BRAND
                     ================================================= -->

                <div class="brand">
                    <div class="brand-symbol">🪲</div>

                    <div class="brand-title">
                        CODEBUSTERS
                    </div>

                    <div class="brand-subtitle">
                        Find. Fix. Deploy.
                    </div>
                </div>

                <!-- =================================================
                     LOGIN SCREEN
                     ================================================= -->

                <section
                    id="login-screen"
                    class="screen active"
                >

                    <h1 class="screen-title">
                        EMPLOYEE LOGIN
                    </h1>

                    <div class="screen-description">
                        Access the CodeBusters employee system.
                    </div>

                    <form id="login-form">

                        <div class="form-group">
                            <label for="login-username">
                                Username
                            </label>

                            <input
                                id="login-username"
                                name="username"
                                type="text"
                                autocomplete="username"
                                placeholder="Enter username"
                                required
                            >
                        </div>

                        <div class="form-group">
                            <label for="login-password">
                                Password
                            </label>

                            <input
                                id="login-password"
                                name="password"
                                type="password"
                                autocomplete="current-password"
                                placeholder="Enter password"
                                required
                            >
                        </div>

                        <button
                            class="primary-button"
                            type="submit"
                        >
                            LOG IN
                        </button>

                        <div class="account-actions">

                            <button
                                id="forgot-password-link"
                                class="secondary-link"
                                type="button"
                            >
                                Forgot Password?
                            </button>

                            <button
                                id="create-employee-link"
                                class="secondary-link"
                                type="button"
                            >
                                Create Employee
                            </button>

                        </div>

                    </form>

                    <div
                        id="login-message"
                        class="message"
                    ></div>

                </section>

                <!-- =================================================
                     PASSWORD RESET SCREEN
                     ================================================= -->

                <section
                    id="reset-screen"
                    class="screen"
                >

                    <h1 class="screen-title">
                        RESET PASSWORD
                    </h1>

                    <div class="screen-description">
                        Verify your account and create a new password.
                    </div>

                    <form id="reset-initiate-form">

                        <div class="form-group">

                            <label for="reset-username">
                                Username
                            </label>

                            <input
                                id="reset-username"
                                type="text"
                                placeholder="Enter username"
                                required
                            >

                        </div>

                        <div class="form-group">

                            <label for="reset-channel">
                                Verification Method
                            </label>

                            <select
                                id="reset-channel"
                                required
                            >
                                <option value="email">
                                    Email
                                </option>

                                <option value="phone">
                                    Phone
                                </option>
                            </select>

                        </div>

                        <button
                            class="primary-button"
                            type="submit"
                        >
                            SEND VERIFICATION CODE
                        </button>

                    </form>

                    <div
                        id="reset-initiate-message"
                        class="message"
                    ></div>

                    <form
                        id="reset-confirm-form"
                        style="margin-top: 22px;"
                    >

                        <div class="form-group">

                            <label for="reset-code">
                                Verification Code
                            </label>

                            <input
                                id="reset-code"
                                type="text"
                                maxlength="6"
                                inputmode="numeric"
                                placeholder="6-digit code"
                                required
                            >

                        </div>

                        <div class="form-group">

                            <label for="reset-password">
                                New Password
                            </label>

                            <input
                                id="reset-password"
                                type="password"
                                minlength="12"
                                maxlength="72"
                                placeholder="Enter new password"
                                required
                            >

                        </div>

                        <button
                            class="primary-button"
                            type="submit"
                        >
                            RESET PASSWORD
                        </button>

                    </form>

                    <div
                        id="reset-confirm-message"
                        class="message"
                    ></div>

                    <button
                        id="reset-back-button"
                        class="back-button"
                        type="button"
                    >
                        BACK TO LOGIN
                    </button>

                </section>

                <!-- =================================================
                     CREATE EMPLOYEE SCREEN
                     ================================================= -->

                <section
                    id="create-employee-screen"
                    class="screen"
                >

                    <h1 class="screen-title">
                        CREATE EMPLOYEE
                    </h1>

                    <div class="screen-description">
                        Create a new CodeBusters employee account.
                        Generated login credentials will be emailed
                        after the employee is created.
                    </div>

                    <form id="create-employee-form">

                        <div class="form-grid">

                            <div class="form-group">

                                <label for="employee-first-name">
                                    First Name
                                </label>

                                <input
                                    id="employee-first-name"
                                    type="text"
                                    placeholder="First name"
                                    required
                                >

                            </div>

                            <div class="form-group">

                                <label for="employee-last-name">
                                    Last Name
                                </label>

                                <input
                                    id="employee-last-name"
                                    type="text"
                                    placeholder="Last name"
                                    required
                                >

                            </div>

                        </div>

                        <div class="form-group">

                            <label for="employee-email">
                                Email
                            </label>

                            <input
                                id="employee-email"
                                type="email"
                                placeholder="employee@example.com"
                                required
                            >

                        </div>

                        <div class="form-group">

                            <label for="employee-phone">
                                Phone Number
                            </label>

                            <input
                                id="employee-phone"
                                type="text"
                                placeholder="Phone number"
                                required
                            >

                        </div>

                        <div class="form-group">

                            <label for="employee-role">
                                Role
                            </label>

                            <select
                                id="employee-role"
                                required
                            >
                                <option value="employee">
                                    Employee
                                </option>

                                <option value="manager">
                                    Manager
                                </option>

                                <option value="admin">
                                    Admin
                                </option>
                            </select>

                        </div>

                        <div class="form-grid">

                            <div class="form-group">

                                <label for="employee-hourly-rate">
                                    Hourly Rate
                                </label>

                                <input
                                    id="employee-hourly-rate"
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    placeholder="20.00"
                                    required
                                >

                            </div>

                            <div class="form-group">

                                <label for="employee-hire-date">
                                    Hire Date
                                </label>

                                <input
                                    id="employee-hire-date"
                                    type="text"
                                    placeholder="MM/DD/YYYY"
                                    required
                                >

                            </div>

                        </div>

                        <div class="form-grid">

                            <div class="form-group">

                                <label for="employee-active">
                                    Active
                                </label>

                                <select
                                    id="employee-active"
                                    required
                                >
                                    <option value="true">
                                        Yes
                                    </option>

                                    <option value="false">
                                        No
                                    </option>
                                </select>

                            </div>

                            <div class="form-group">

                                <label for="employee-term-date">
                                    Term Date
                                </label>

                                <input
                                    id="employee-term-date"
                                    type="text"
                                    placeholder="MM/DD/YYYY"
                                >

                            </div>

                        </div>

                        <button
                            class="primary-button"
                            type="submit"
                        >
                            CREATE EMPLOYEE
                        </button>

                    </form>

                    <div
                        id="create-employee-message"
                        class="message"
                    ></div>

                    <button
                        id="create-employee-back-button"
                        class="back-button"
                        type="button"
                    >
                        BACK TO LOGIN
                    </button>

                </section>

            </section>

        </main>

    </div>

    <!-- =============================================================
         STICKY FOOTER
         ============================================================= -->

    <footer class="footer">

        <div class="footer-title">
            CODEBUSTERS
        </div>

        <div class="footer-subtitle">
            FIND. FIX. DEPLOY.
        </div>

    </footer>

</div>

<script>

    /*
     * -------------------------------------------------------------
     * SCREEN NAVIGATION
     * -------------------------------------------------------------
     */

    const loginScreen =
        document.getElementById("login-screen");

    const resetScreen =
        document.getElementById("reset-screen");

    const createEmployeeScreen =
        document.getElementById(
            "create-employee-screen"
        );

    function showScreen(screen) {

        loginScreen.classList.remove("active");
        resetScreen.classList.remove("active");
        createEmployeeScreen.classList.remove("active");

        screen.classList.add("active");

        const scrollContainer =
            document.querySelector(".page-scroll");

        if (scrollContainer) {
            scrollContainer.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        }
    }

    /*
     * -------------------------------------------------------------
     * MESSAGES
     * -------------------------------------------------------------
     */

    function showMessage(
        elementId,
        message,
        type
    ) {

        const element =
            document.getElementById(elementId);

        element.textContent = message;

        element.className =
            "message visible " + type;
    }

    function clearMessage(elementId) {

        const element =
            document.getElementById(elementId);

        element.textContent = "";
        element.className = "message";
    }

    /*
     * -------------------------------------------------------------
     * LOGIN
     * -------------------------------------------------------------
     */

    document
        .getElementById("login-form")
        .addEventListener("submit", async function(event) {

            event.preventDefault();

            clearMessage("login-message");

            const username =
                document.getElementById(
                    "login-username"
                ).value.trim();

            const password =
                document.getElementById(
                    "login-password"
                ).value;

            const body =
                new URLSearchParams();

            body.append(
                "username",
                username
            );

            body.append(
                "password",
                password
            );

            try {

                const response =
                    await fetch(
                        "/auth/login",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/x-www-form-urlencoded"
                            },

                            body: body.toString()
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Login failed."
                    );
                }

                sessionStorage.setItem(
                    "access_token",
                    data.access_token
                );

                showMessage(
                    "login-message",
                    data.must_change_password
                        ? "LOGIN SUCCESSFUL — PLEASE CHANGE YOUR TEMPORARY PASSWORD."
                        : "LOGIN SUCCESSFUL.",
                    "success"
                );

            } catch (error) {

                showMessage(
                    "login-message",
                    error.message,
                    "error"
                );
            }
        });

    /*
     * -------------------------------------------------------------
     * FORGOT PASSWORD
     * -------------------------------------------------------------
     */

    document
        .getElementById("forgot-password-link")
        .addEventListener("click", function() {

            clearMessage("login-message");
            clearMessage("reset-initiate-message");
            clearMessage("reset-confirm-message");

            showScreen(resetScreen);
        });

    document
        .getElementById("reset-initiate-form")
        .addEventListener("submit", async function(event) {

            event.preventDefault();

            clearMessage(
                "reset-initiate-message"
            );

            const username =
                document.getElementById(
                    "reset-username"
                ).value.trim();

            const channel =
                document.getElementById(
                    "reset-channel"
                ).value;

            try {

                const response =
                    await fetch(
                        "/password-reset/initiate",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                username: username,
                                channel: channel
                            })
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Unable to send verification code."
                    );
                }

                showMessage(
                    "reset-initiate-message",
                    "VERIFICATION CODE SENT.",
                    "success"
                );

            } catch (error) {

                showMessage(
                    "reset-initiate-message",
                    error.message,
                    "error"
                );
            }

        });

    document
        .getElementById("reset-confirm-form")
        .addEventListener("submit", async function(event) {

            event.preventDefault();

            clearMessage(
                "reset-confirm-message"
            );

            const username =
                document.getElementById(
                    "reset-username"
                ).value.trim();

            const code =
                document.getElementById(
                    "reset-code"
                ).value.trim();

            const newPassword =
                document.getElementById(
                    "reset-password"
                ).value;

            try {

                const response =
                    await fetch(
                        "/password-reset/confirm",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                username: username,
                                code: code,
                                new_password: newPassword
                            })
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Password reset failed."
                    );
                }

                showMessage(
                    "reset-confirm-message",
                    "PASSWORD RESET SUCCESSFUL.",
                    "success"
                );

            } catch (error) {

                showMessage(
                    "reset-confirm-message",
                    error.message,
                    "error"
                );
            }

        });

    document
        .getElementById("reset-back-button")
        .addEventListener("click", function() {

            showScreen(loginScreen);

        });

    /*
     * -------------------------------------------------------------
     * CREATE EMPLOYEE
     * -------------------------------------------------------------
     */

    document
        .getElementById("create-employee-link")
        .addEventListener("click", function() {

            const accessToken =
                sessionStorage.getItem(
                    "access_token"
                );

            if (!accessToken) {

                showMessage(
                    "login-message",
                    "PLEASE LOG IN FIRST. ONLY AN AUTHENTICATED MANAGER CAN CREATE EMPLOYEES.",
                    "error"
                );

                return;
            }

            clearMessage("login-message");
            clearMessage(
                "create-employee-message"
            );

            showScreen(createEmployeeScreen);

        });

    /*
     * Keep term date disabled unless employee is inactive.
     */

    const activeSelect =
        document.getElementById(
            "employee-active"
        );

    const termDateInput =
        document.getElementById(
            "employee-term-date"
        );

    function updateTermDateState() {

        const isActive =
            activeSelect.value === "true";

        termDateInput.disabled =
            isActive;

        if (isActive) {
            termDateInput.value = "";
        }

    }

    activeSelect.addEventListener(
        "change",
        updateTermDateState
    );

    updateTermDateState();

    document
        .getElementById("create-employee-form")
        .addEventListener("submit", async function(event) {

            event.preventDefault();

            clearMessage(
                "create-employee-message"
            );

            const accessToken =
                sessionStorage.getItem(
                    "access_token"
                );

            if (!accessToken) {

                showMessage(
                    "create-employee-message",
                    "YOUR LOGIN SESSION HAS EXPIRED. PLEASE LOG IN AGAIN.",
                    "error"
                );

                showScreen(loginScreen);

                return;
            }

            const employeeData = {

                active:
                    document.getElementById(
                        "employee-active"
                    ).value === "true",

                first_name:
                    document.getElementById(
                        "employee-first-name"
                    ).value.trim(),

                last_name:
                    document.getElementById(
                        "employee-last-name"
                    ).value.trim(),

                email:
                    document.getElementById(
                        "employee-email"
                    ).value.trim(),

                phone_number:
                    document.getElementById(
                        "employee-phone"
                    ).value.trim(),

                role:
                    document.getElementById(
                        "employee-role"
                    ).value,

                hourly_rate:
                    Number(
                        document.getElementById(
                            "employee-hourly-rate"
                        ).value
                    ),

                hire_date:
                    document.getElementById(
                        "employee-hire-date"
                    ).value.trim(),

                term_date:
                    document.getElementById(
                        "employee-term-date"
                    ).value.trim() || null
            };

            try {

                const response =
                    await fetch(
                        "/employees",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Authorization":
                                    "Bearer " +
                                    accessToken
                            },

                            body:
                                JSON.stringify(
                                    employeeData
                                )
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Employee creation failed."
                    );
                }

                showMessage(
                    "create-employee-message",
                    "EMPLOYEE CREATED SUCCESSFULLY. LOGIN CREDENTIALS HAVE BEEN SENT TO THE EMPLOYEE.",
                    "success"
                );

                document
                    .getElementById(
                        "create-employee-form"
                    )
                    .reset();

                updateTermDateState();

            } catch (error) {

                showMessage(
                    "create-employee-message",
                    error.message,
                    "error"
                );
            }

        });

    /*
     * -------------------------------------------------------------
     * BACK TO LOGIN
     * -------------------------------------------------------------
     */

    document
        .getElementById(
            "create-employee-back-button"
        )
        .addEventListener("click", function() {

            showScreen(loginScreen);

        });

</script>

</body>
</html>
"""


@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page():
    """Render the CodeBusters employee login page."""
    return HTMLResponse(
        content=LOGIN_PAGE
    )
