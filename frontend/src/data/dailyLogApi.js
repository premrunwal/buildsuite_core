import { frappeRequest } from "frappe-ui-frappe-request";
import { parseFrappeError } from "@/utils/frappeError";

async function call(method, args) {
	try {
		return await frappeRequest({
			url: `buildsuite_core.api.daily_log.${method}`,
			params: args || {},
		});
	} catch (err) {
		throw new Error(parseFrappeError(err).summary || "Request failed.");
	}
}

export async function getDailyLogs(filters = {}) {
	try {
		return await call("get_daily_logs", filters);
	} catch (e) {
		console.warn("Failed to fetch daily logs:", e);
		return [];
	}
}

export async function getSitePhotos(filters = {}) {
	try {
		return await call("get_site_photos", filters);
	} catch (e) {
		console.warn("Failed to fetch site photos:", e);
		return [];
	}
}

export async function createDailyLog(payload) {
	return await call("create_daily_log", payload);
}
