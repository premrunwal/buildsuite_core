<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import LogoIcon from "@/components/LogoIcon.vue";
import { getServerUrl, loginWithCredentials, getStoredAuth } from "@/utils/mobile";
import { useSessionStore } from "@/stores/session";
import { useDataStore } from "@/stores";

const router = useRouter();
const route = useRoute();
const sessionStore = useSessionStore();
const dataStore = useDataStore();

// 2 Types of Auth: 'admin' and 'supervisor'
const authType = ref("supervisor"); // default to field supervisor for mobile users

const serverUrl = ref("");
const username = ref("");
const password = ref("");
const showPassword = ref(false);
const supervisorRole = ref("BuildSuite Site Engineer");
const isLoading = ref(false);
const errorMessage = ref("");

const supervisorRoles = [
	{ label: "Site Engineer", value: "BuildSuite Site Engineer" },
	{ label: "Site Supervisor / Foreman", value: "BuildSuite Foreman" },
	{ label: "Project Manager", value: "BuildSuite PM" },
	{ label: "Store Keeper", value: "BuildSuite Store Keeper" },
];

onMounted(() => {
	const currentServer = getServerUrl();
	if (!currentServer) {
		router.replace({ name: "server-url", query: { redirect: "/login" } });
		return;
	}
	serverUrl.value = currentServer;

	const stored = getStoredAuth();
	if (stored.authType) {
		authType.value = stored.authType;
	}
	if (stored.user && stored.user !== "Guest") {
		username.value = stored.user;
	}
});

function quickFill(user, pass) {
	username.value = user;
	password.value = pass;
}

function onChangeServer() {
	router.push({ name: "server-url", query: { redirect: "/login" } });
}

async function handleLogin() {
	errorMessage.value = "";
	if (!username.value.trim() || !password.value) {
		errorMessage.value = "Please enter both username and password.";
		return;
	}

	isLoading.value = true;
	try {
		const authResult = await loginWithCredentials(serverUrl.value, {
			username: username.value.trim(),
			password: password.value,
			authType: authType.value,
		});

		sessionStore.user = authResult.user;
		sessionStore.authenticated = true;

		// Refresh session store with new access context
		try {
			await sessionStore.recheckAccess();
		} catch (e) {
			console.warn("[login] Access recheck warning", e);
		}

		// Initialize data stores
		try {
			await Promise.all([
				dataStore.loadCompanies(),
				dataStore.loadWorkspaces(),
				dataStore.loadProjectSettings(),
			]);
		} catch (e) {
			console.warn("[login] Preload warning", e);
		}

		const redirect = route.query.redirect;
		if (redirect && redirect !== "/login" && redirect !== "/server-url") {
			router.push(redirect);
		} else {
			router.push("/home");
		}
	} catch (err) {
		errorMessage.value = err.message || "Authentication failed. Check credentials.";
	} finally {
		isLoading.value = false;
	}
}
</script>

<template>
	<div class="min-h-screen bg-ink-950 text-white flex flex-col justify-center px-4 py-8 sm:px-6">
		<div class="max-w-md w-full mx-auto space-y-6">
			<!-- Header -->
			<div class="text-center space-y-2">
				<div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-500/10 border border-brand-500/30 text-brand-400">
					<LogoIcon class="w-8 h-8" />
				</div>
				<h1 class="text-2xl font-bold tracking-tight text-ink-50">BuildSuite Core</h1>
				<p class="text-xs text-ink-400">Mobile Site Execution & Management</p>
			</div>

			<!-- Connected Server Badge -->
			<div class="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-ink-900 border border-ink-800 text-xs">
				<div class="flex items-center gap-2 truncate mr-2">
					<span class="w-2 h-2 rounded-full bg-success-400 flex-shrink-0 animate-pulse"></span>
					<span class="text-ink-400">Server:</span>
					<span class="font-mono text-ink-200 truncate">{{ serverUrl }}</span>
				</div>
				<button
					type="button"
					class="text-brand-400 hover:text-brand-300 font-medium text-xs flex-shrink-0 px-2 py-1 rounded hover:bg-ink-800 active:bg-ink-700"
					@click="onChangeServer"
				>
					Change
				</button>
			</div>

			<!-- Auth Mode Selector (2 Types: Admin vs Supervisors) -->
			<div class="grid grid-cols-2 p-1 bg-ink-900 border border-ink-800 rounded-2xl gap-1">
				<button
					type="button"
					:class="[
						'flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-semibold transition-all min-h-[44px]',
						authType === 'supervisor'
							? 'bg-brand-500 text-white shadow-md shadow-brand-500/20'
							: 'text-ink-400 hover:text-ink-200 hover:bg-ink-850'
					]"
					@click="authType = 'supervisor'"
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
					</svg>
					<span>Supervisors</span>
				</button>

				<button
					type="button"
					:class="[
						'flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-semibold transition-all min-h-[44px]',
						authType === 'admin'
							? 'bg-brand-500 text-white shadow-md shadow-brand-500/20'
							: 'text-ink-400 hover:text-ink-200 hover:bg-ink-850'
					]"
					@click="authType = 'admin'"
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
					</svg>
					<span>Administrator</span>
				</button>
			</div>

			<!-- Login Card -->
			<div class="bg-ink-900 border border-ink-800 rounded-2xl p-6 shadow-xl space-y-4">
				<div class="border-b border-ink-800 pb-3">
					<h2 class="text-base font-semibold text-ink-100 flex items-center gap-2">
						<span v-if="authType === 'supervisor'">Site Supervisor Login</span>
						<span v-else>Administrator Login</span>
					</h2>
					<p class="text-xs text-ink-400 mt-0.5">
						<span v-if="authType === 'supervisor'">Daily attendance, task progress, petty cash, and site reports.</span>
						<span v-else>System setup, company management, and configuration.</span>
					</p>
				</div>

				<!-- Field / Supervisor Preset Selector -->
				<div v-if="authType === 'supervisor'" class="space-y-1.5">
					<label class="block text-xs font-semibold uppercase tracking-wider text-ink-400">
						Site Role Profile
					</label>
					<select
						v-model="supervisorRole"
						class="w-full bg-ink-950 border border-ink-700 rounded-xl px-4 py-3 text-ink-100 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-sm"
					>
						<option v-for="role in supervisorRoles" :key="role.value" :value="role.value">
							{{ role.label }}
						</option>
					</select>
				</div>

				<!-- Username Field -->
				<div class="space-y-1.5">
					<label class="block text-xs font-semibold uppercase tracking-wider text-ink-400">
						Username or Email
					</label>
					<input
						v-model="username"
						type="text"
						autocomplete="username"
						placeholder="username or email@example.com"
						class="w-full bg-ink-950 border border-ink-700 rounded-xl px-4 py-3 text-ink-100 placeholder-ink-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-base"
						@keydown.enter="handleLogin"
					/>
				</div>

				<!-- Password Field -->
				<div class="space-y-1.5">
					<div class="flex items-center justify-between">
						<label class="block text-xs font-semibold uppercase tracking-wider text-ink-400">
							Password
						</label>
						<button
							type="button"
							class="text-xs text-ink-400 hover:text-ink-200"
							@click="showPassword = !showPassword"
						>
							{{ showPassword ? "Hide" : "Show" }}
						</button>
					</div>
					<input
						v-model="password"
						:type="showPassword ? 'text' : 'password'"
						autocomplete="current-password"
						placeholder="••••••••"
						class="w-full bg-ink-950 border border-ink-700 rounded-xl px-4 py-3 text-ink-100 placeholder-ink-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-base font-mono"
						@keydown.enter="handleLogin"
					/>
				</div>

				<!-- Error alert -->
				<div v-if="errorMessage" class="p-3.5 rounded-xl bg-danger-500/10 border border-danger-500/30 text-danger-400 text-xs flex items-start gap-2.5">
					<svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<span>{{ errorMessage }}</span>
				</div>

				<!-- Login button -->
				<button
					type="button"
					:disabled="isLoading"
					class="w-full min-h-[48px] flex items-center justify-center font-medium rounded-xl bg-brand-500 hover:bg-brand-600 active:bg-brand-700 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-brand-500/25 mt-2"
					@click="handleLogin"
				>
					<svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					<span>{{ isLoading ? "Signing in..." : "Sign In" }}</span>
				</button>
			</div>

			<!-- Dev quick fills if in dev or localhost -->
			<div v-if="serverUrl.includes('localhost') || serverUrl.includes('127.0.0.1')" class="p-3 bg-ink-900/60 border border-ink-800/80 rounded-xl text-xs space-y-2">
				<p class="text-ink-400 font-medium">Quick Fill (Dev / Test):</p>
				<div class="flex flex-wrap gap-2">
					<button
						type="button"
						class="px-2.5 py-1 bg-ink-800 hover:bg-ink-700 rounded-lg text-ink-200"
						@click="quickFill('Administrator', 'admin')"
					>
						Admin (Administrator)
					</button>
					<button
						type="button"
						class="px-2.5 py-1 bg-ink-800 hover:bg-ink-700 rounded-lg text-ink-200"
						@click="quickFill('test_site_engineer@example.com', 'site123')"
					>
						Supervisor (Site Eng)
					</button>
				</div>
			</div>
		</div>
	</div>
</template>
