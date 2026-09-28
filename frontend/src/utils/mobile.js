import { Capacitor } from "@capacitor/core";
import { Preferences } from "@capacitor/preferences";
import { App as CapApp } from "@capacitor/app";
import { StatusBar, Style } from "@capacitor/status-bar";
import { SplashScreen } from "@capacitor/splash-screen";
import { Network } from "@capacitor/network";
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";
import { Geolocation } from "@capacitor/geolocation";

const PREF_KEY_SERVER_URL = "bs_server_url";
const PREF_KEY_API_KEY = "bs_api_key";
const PREF_KEY_API_SECRET = "bs_api_secret";
const PREF_KEY_USER = "bs_session_user";
const PREF_KEY_AUTH_TYPE = "bs_auth_type"; // 'admin' | 'supervisor'

// In-memory cache of stored credentials for synchronous fetch interception
let cachedServerUrl = "";
let cachedApiKey = "";
let cachedApiSecret = "";
let cachedUser = "";
let cachedAuthType = "";
let isInitialized = false;
let sessionExpiredCallback = null;

export function isCapacitor() {
	return Capacitor.isNativePlatform();
}

export function isMobileApp() {
	if (isCapacitor()) return true;
	if (typeof __IS_MOBILE_BUILD__ !== "undefined" && __IS_MOBILE_BUILD__) return true;
	if (typeof window !== "undefined") {
		const proto = window.location.protocol;
		if (proto === "capacitor:" || proto === "file:") return true;
		if (window.location.search.includes("mobile=1") || localStorage.getItem("bs_force_mobile") === "1") return true;
	}
	return false;
}

export async function initMobileStorage() {
	if (isInitialized) return;

	try {
		const [serverUrlRes, keyRes, secretRes, userRes, typeRes] = await Promise.all([
			Preferences.get({ key: PREF_KEY_SERVER_URL }),
			Preferences.get({ key: PREF_KEY_API_KEY }),
			Preferences.get({ key: PREF_KEY_API_SECRET }),
			Preferences.get({ key: PREF_KEY_USER }),
			Preferences.get({ key: PREF_KEY_AUTH_TYPE }),
		]);

		cachedServerUrl = (serverUrlRes.value || "").trim().replace(/\/+$/, "");
		cachedApiKey = (keyRes.value || "").trim();
		cachedApiSecret = (secretRes.value || "").trim();
		cachedUser = (userRes.value || "").trim();
		cachedAuthType = (typeRes.value || "").trim();

		if (cachedUser) {
			window.session_user = cachedUser;
		}
	} catch (e) {
		console.warn("[mobile] Failed to read preferences from storage", e);
	}

	isInitialized = true;
}

export function getServerUrl() {
	return cachedServerUrl;
}

export async function setServerUrl(url) {
	const clean = (url || "").trim().replace(/\/+$/, "");
	cachedServerUrl = clean;
	await Preferences.set({ key: PREF_KEY_SERVER_URL, value: clean });
}

export function getStoredAuth() {
	return {
		apiKey: cachedApiKey,
		apiSecret: cachedApiSecret,
		user: cachedUser,
		authType: cachedAuthType,
		hasToken: Boolean(cachedApiKey && cachedApiSecret),
	};
}

export async function setStoredAuth({ apiKey, apiSecret, user, authType }) {
	cachedApiKey = apiKey || "";
	cachedApiSecret = apiSecret || "";
	cachedUser = user || "";
	cachedAuthType = authType || "supervisor";

	if (cachedUser) {
		window.session_user = cachedUser;
	}

	await Promise.all([
		Preferences.set({ key: PREF_KEY_API_KEY, value: cachedApiKey }),
		Preferences.set({ key: PREF_KEY_API_SECRET, value: cachedApiSecret }),
		Preferences.set({ key: PREF_KEY_USER, value: cachedUser }),
		Preferences.set({ key: PREF_KEY_AUTH_TYPE, value: cachedAuthType }),
	]);
}

export async function clearStoredAuth() {
	cachedApiKey = "";
	cachedApiSecret = "";
	cachedUser = "";
	window.session_user = "Guest";

	await Promise.all([
		Preferences.remove({ key: PREF_KEY_API_KEY }),
		Preferences.remove({ key: PREF_KEY_API_SECRET }),
		Preferences.remove({ key: PREF_KEY_USER }),
	]);
}

export function onSessionExpired(callback) {
	sessionExpiredCallback = callback;
}

export function notifySessionExpired() {
	if (sessionExpiredCallback) {
		sessionExpiredCallback();
	}
}

/**
 * Validate connection to a Frappe server via ping.
 */
export async function validateServerUrl(rawUrl) {
	const url = (rawUrl || "").trim().replace(/\/+$/, "");
	if (!url || (!url.startsWith("http://") && !url.startsWith("https://"))) {
		throw new Error("Please enter a valid URL starting with http:// or https://");
	}

	const pingEndpoint = `${url}/api/method/ping`;
	const controller = new AbortController();
	const timeout = setTimeout(() => controller.abort(), 10000);

	try {
		const res = await fetch(pingEndpoint, {
			method: "GET",
			signal: controller.signal,
			headers: { Accept: "application/json" },
		});
		clearTimeout(timeout);

		if (!res.ok) {
			throw new Error(`Server returned HTTP ${res.status}`);
		}

		const data = await res.json();
		if (data.message !== "pong" && !data.message) {
			throw new Error("Not a valid Frappe/ERPNext server response");
		}
		return true;
	} catch (err) {
		clearTimeout(timeout);
		if (err.name === "AbortError") {
			throw new Error("Connection timed out. Check network or server URL.");
		}
		throw new Error(err.message || "Failed to reach server");
	}
}

/**
 * Perform login and exchange for API Token
 */
export async function loginWithCredentials(serverUrl, { username, password, authType = "supervisor" }) {
	const cleanUrl = (serverUrl || cachedServerUrl || "").trim().replace(/\/+$/, "");
	if (!cleanUrl) throw new Error("Server URL not configured");

	const mobileLoginRes = await fetch(`${cleanUrl}/api/method/buildsuite_core.api.mobile_auth.mobile_login`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
		},
		body: JSON.stringify({ usr: username, pwd: password }),
	});

	if (!mobileLoginRes.ok) {
		let errMsg = "Invalid username or password";
		try {
			const errData = await mobileLoginRes.json();
			if (errData.message) errMsg = errData.message;
			else if (errData._server_messages) {
				const parsed = JSON.parse(errData._server_messages);
				if (Array.isArray(parsed) && parsed.length > 0) {
					const inner = JSON.parse(parsed[0]);
					errMsg = inner.message || errMsg;
				}
			}
		} catch {
			// ignore
		}
		throw new Error(errMsg);
	}

	const resData = await mobileLoginRes.json();
	const payload = resData.message || resData;
	const apiKey = payload.api_key || "";
	const apiSecret = payload.api_secret || "";
	const user = payload.user || username;

	if (!apiKey || !apiSecret) {
		throw new Error("Server failed to generate API credentials for this user.");
	}

	await setStoredAuth({
		apiKey,
		apiSecret,
		user,
		authType,
	});

	return { user, apiKey, apiSecret, authType };
}

/**
 * Resolve an API or asset URL against the configured server URL.
 */
export function resolveApiUrl(rawUrl) {
	if (!rawUrl || typeof rawUrl !== "string") return rawUrl;
	if (rawUrl.startsWith("http://") || rawUrl.startsWith("https://") || rawUrl.startsWith("data:") || rawUrl.startsWith("blob:")) {
		return rawUrl;
	}

	const serverUrl = cachedServerUrl;
	if (!serverUrl) return rawUrl;

	const cleanPath = rawUrl.startsWith("/") ? rawUrl : `/${rawUrl}`;
	return `${serverUrl}${cleanPath}`;
}

/**
 * Native plugin helpers
 */
export async function initNativeFeatures() {
	if (!isCapacitor()) return;

	try {
		await StatusBar.setStyle({ style: Style.Dark });
		await StatusBar.setBackgroundColor({ color: "#1A1A1A" });
	} catch {
		// StatusBar not available on web
	}

	try {
		await SplashScreen.hide();
	} catch {
		// SplashScreen not available on web
	}
}

export function registerHardwareBackButton(onBack) {
	if (!isCapacitor()) return () => {};

	const listener = CapApp.addListener("backButton", (event) => {
		if (onBack) {
			onBack(event);
		}
	});

	return () => {
		listener.then((sub) => sub.remove()).catch(() => {});
	};
}

export async function getNetworkStatus() {
	try {
		return await Network.getStatus();
	} catch {
		return { connected: navigator.onLine, connectionType: "unknown" };
	}
}

export function onNetworkChange(callback) {
	try {
		const listener = Network.addListener("networkStatusChange", callback);
		return () => {
			listener.then((sub) => sub.remove()).catch(() => {});
		};
	} catch {
		window.addEventListener("online", () => callback({ connected: true }));
		window.addEventListener("offline", () => callback({ connected: false }));
		return () => {};
	}
}

export async function takePhoto() {
	try {
		const image = await Camera.getPhoto({
			quality: 85,
			allowEditing: false,
			resultType: CameraResultType.Uri,
			source: CameraSource.Prompt, // Allows choosing between Camera or Photo Library
		});
		return image;
	} catch (e) {
		console.warn("[mobile] Camera capture cancelled or failed", e);
		return null;
	}
}

export async function getCurrentCoordinates() {
	try {
		const position = await Geolocation.getCurrentPosition({
			enableHighAccuracy: true,
			timeout: 10000,
		});
		return {
			latitude: position.coords.latitude,
			longitude: position.coords.longitude,
		};
	} catch (e) {
		console.warn("[mobile] Geolocation failed", e);
		return null;
	}
}

/**
 * Install global fetch interceptor to seamlessly prepend server URL,
 * attach Authorization token, set X-Frappe-Site-Name, and catch 401s.
 */
let interceptorInstalled = false;
export function setupFetchInterceptor() {
	if (interceptorInstalled || typeof window === "undefined") return;
	interceptorInstalled = true;

	const originalFetch = window.fetch;
	window.fetch = async function (input, init = {}) {
		let url = typeof input === "string" ? input : input instanceof Request ? input.url : "";
		const serverUrl = cachedServerUrl;

		// Check if this is an API call that needs resolution
		const isApi = url.includes("/api/") || url.startsWith("/api") || (typeof input === "string" && !url.startsWith("http") && !url.startsWith("./") && !url.startsWith("/assets"));

		if (isApi && serverUrl && !url.startsWith("http")) {
			url = resolveApiUrl(url);
		}

		// Prepare headers
		const headers = new Headers(init.headers || (input instanceof Request ? input.headers : {}));

		// Attach token auth if we have keys and target is our configured server
		if (cachedApiKey && cachedApiSecret) {
			if (!headers.has("Authorization")) {
				headers.set("Authorization", `token ${cachedApiKey}:${cachedApiSecret}`);
			}
		}

		// Inject X-Frappe-Site-Name from server URL host if target is cross-origin
		if (serverUrl) {
			try {
				const serverHost = new URL(serverUrl).hostname;
				if (!headers.has("X-Frappe-Site-Name")) {
					headers.set("X-Frappe-Site-Name", serverHost);
				}
			} catch {
				// ignore
			}
		}

		const newInit = {
			...init,
			headers,
			credentials: init.credentials || "include",
		};

		const finalInput = input instanceof Request ? new Request(url, newInit) : url;

		try {
			const res = await originalFetch.call(this, finalInput, newInit);

			// Handle 401 Unauthorized for authenticated session requests
			if (res.status === 401 && !url.includes("/api/method/login") && !url.includes("/api/method/ping")) {
				console.warn("[mobile] Received 401 Unauthorized from server:", url);
				notifySessionExpired();
			}

			return res;
		} catch (error) {
			throw error;
		}
	};
}
