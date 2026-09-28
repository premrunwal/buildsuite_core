<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { useDataStore } from "@/stores";
import { useSessionStore } from "@/stores/session";
import { useUserNames } from "@/composables/useUserNames";
import { useActiveCompany } from "@/composables/useActiveCompany";
import { fmtCompactINR } from "@/utils/format";
import { getHomeDashboard } from "@/data/homeDashboardApi";

const store = useDataStore();
const session = useSessionStore();
const { userName: resolveUserName } = useUserNames();
const activeCompany = useActiveCompany();

const dash = ref(null);
async function load() {
	try {
		dash.value = await getHomeDashboard();
	} catch {
		dash.value = null;
	}
}
onMounted(load);
watch(activeCompany, load);

const snapshot = computed(() => dash.value?.snapshot || []);

const now = new Date();
const greeting = computed(() => {
	const hour = now.getHours();
	if (hour < 12) return "Good Morning";
	if (hour < 18) return "Good Afternoon";
	return "Good Evening";
});

const userName = computed(() => {
	const id = session.user && session.user !== "Guest" ? session.user : null;
	return (id && resolveUserName(id)) || store.user?.name || "Administrator";
});

const roleLabel = computed(() =>
	store.isAdmin ? "System Manager" : store.currentRole?.name || "Site Engineer"
);

const dateLabel = computed(() =>
	new Intl.DateTimeFormat("en-US", {
		weekday: "short",
		day: "numeric",
		month: "short",
		year: "numeric",
	}).format(now)
);

const primaryActions = [
	{
		title: "Daily Logs",
		desc: "Record daily site progress, weather & blockers",
		to: "/daily-logs",
		icon: "file-text",
		color: "bg-blue-50 text-blue-600 border-blue-200",
		btnText: "Open Logs",
	},
	{
		title: "Site Photos",
		desc: "Capture & inspect site progress photographs",
		to: "/site-photos",
		icon: "camera",
		color: "bg-emerald-50 text-emerald-600 border-emerald-200",
		btnText: "View Photos",
	},
	{
		title: "Field Attendance",
		desc: "Daily worker muster, crews & labor attendance",
		to: "/field-attendance",
		icon: "users",
		color: "bg-purple-50 text-purple-600 border-purple-200",
		btnText: "Mark Attendance",
	},
	{
		title: "Projects",
		desc: "View active construction projects & milestones",
		to: "/projects",
		icon: "building",
		color: "bg-amber-50 text-amber-600 border-amber-200",
		btnText: "View Projects",
	},
	{
		title: "Material Consumption",
		desc: "Log daily raw materials & site issues",
		to: "/material-consumption",
		icon: "package",
		color: "bg-cyan-50 text-cyan-600 border-cyan-200",
		btnText: "Log Consumption",
	},
	{
		title: "Petty Cash & Expenses",
		desc: "Record site expenses & petty cash requests",
		to: "/project-finance/petty-cash",
		icon: "cash",
		color: "bg-slate-50 text-slate-700 border-slate-200",
		btnText: "Manage Cash",
	},
];
</script>

<template>
	<div class="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8">
		<!-- Minimal Professional Header -->
		<div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-wrap items-center justify-between gap-4">
			<div>
				<div class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
					{{ greeting }}
				</div>
				<h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">
					{{ userName }}
				</h1>
				<div class="flex items-center gap-2 mt-2 text-xs text-slate-500 font-medium">
					<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
						{{ roleLabel }}
					</span>
					<span>·</span>
					<span>{{ dateLabel }}</span>
				</div>
			</div>
			<div class="flex items-center gap-3">
				<RouterLink
					to="/daily-logs/new"
					class="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl shadow-xs transition-all flex items-center gap-2 cursor-pointer"
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					<span>File Daily Log</span>
				</RouterLink>
				<RouterLink
					to="/site-photos"
					class="px-4 py-2.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold rounded-xl shadow-xs transition-all flex items-center gap-2 cursor-pointer"
				>
					<svg class="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
					</svg>
					<span>Take Photo</span>
				</RouterLink>
			</div>
		</div>

		<!-- Clean KPI Overview Grid -->
		<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
			<div
				v-for="m in snapshot"
				:key="m.label"
				class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between"
			>
				<div class="text-[11px] uppercase tracking-wider font-bold text-slate-400 mb-2 truncate">
					{{ m.label }}
				</div>
				<div class="text-2xl sm:text-3xl font-extrabold text-slate-900 font-mono tracking-tight">
					{{ m.format === 'currency' ? fmtCompactINR(m.value) : m.value }}
				</div>
			</div>
		</div>

		<!-- Main Workspace Modules Grid -->
		<div>
			<div class="flex items-center justify-between mb-4 px-1">
				<h2 class="text-sm font-bold uppercase tracking-wider text-slate-700">Site Workspace</h2>
				<span class="text-xs font-medium text-slate-400">Core Modules</span>
			</div>
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
				<RouterLink
					v-for="item in primaryActions"
					:key="item.to"
					:to="item.to"
					class="bg-white border border-slate-200 hover:border-slate-300 hover:shadow-md rounded-2xl p-5 transition-all duration-200 flex flex-col justify-between group cursor-pointer"
				>
					<div>
						<div class="flex items-center justify-between mb-3">
							<div class="w-10 h-10 rounded-xl flex items-center justify-center border" :class="item.color">
								<svg v-if="item.icon === 'file-text'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
								<svg v-else-if="item.icon === 'camera'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
									<circle cx="12" cy="13" r="4" stroke-width="2" />
								</svg>
								<svg v-else-if="item.icon === 'users'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
								</svg>
								<svg v-else-if="item.icon === 'building'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
								</svg>
								<svg v-else-if="item.icon === 'package'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
								</svg>
								<svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
							</div>
							<span class="text-xs font-semibold text-slate-400 group-hover:text-slate-900 transition-colors flex items-center gap-1">
								{{ item.btnText }} →
							</span>
						</div>
						<h3 class="text-base font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">
							{{ item.title }}
						</h3>
						<p class="text-xs text-slate-500 leading-relaxed">
							{{ item.desc }}
						</p>
					</div>
				</RouterLink>
			</div>
		</div>
	</div>
</template>
