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
const searchQuery = ref("");
const selectedCategory = ref("all");

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

const categories = [
	{ id: "all", label: "All Modules" },
	{ id: "site", label: "Site Execution" },
	{ id: "workforce", label: "Workforce & Muster" },
	{ id: "procurement", label: "Procurement & Inventory" },
	{ id: "finance", label: "Financials & Subcontracts" },
	{ id: "estimation", label: "Estimation & Reports" },
];

const allModules = [
	// Site Execution
	{
		title: "Daily Logs",
		desc: "Record daily site progress, weather conditions & blockers",
		to: "/daily-logs",
		icon: "file-text",
		category: "site",
		color: "bg-blue-50 text-blue-600 border-blue-200",
		btnText: "Open Logs",
	},
	{
		title: "Site Photos",
		desc: "Capture & inspect multi-photo site progress logs",
		to: "/site-photos",
		icon: "camera",
		category: "site",
		color: "bg-emerald-50 text-emerald-600 border-emerald-200",
		btnText: "View Photos",
	},
	{
		title: "Projects",
		desc: "View active construction projects, milestones & teams",
		to: "/projects",
		icon: "building",
		category: "site",
		color: "bg-amber-50 text-amber-600 border-amber-200",
		btnText: "View Projects",
	},
	{
		title: "Tasks",
		desc: "Task assignments, execution progress & deadlines",
		to: "/tasks",
		icon: "check-circle",
		category: "site",
		color: "bg-indigo-50 text-indigo-600 border-indigo-200",
		btnText: "View Tasks",
	},
	{
		title: "Task Progress Entries",
		desc: "File & inspect detailed task progress entries",
		to: "/progress-entries",
		icon: "file-text",
		category: "site",
		color: "bg-cyan-50 text-cyan-600 border-cyan-200",
		btnText: "Progress List",
	},
	{
		title: "Schedule",
		desc: "Project Gantt timelines & stage dependencies",
		to: "/schedule",
		icon: "calendar",
		category: "site",
		color: "bg-teal-50 text-teal-600 border-teal-200",
		btnText: "View Schedule",
	},
	{
		title: "Stage Planning",
		desc: "Phase milestone planning & stage reviews",
		to: "/stage-plannings",
		icon: "layout-grid",
		category: "site",
		color: "bg-violet-50 text-violet-600 border-violet-200",
		btnText: "Stage List",
	},
	{
		title: "Scope Change Orders (SCO)",
		desc: "Raise & approve scope variations & extra work",
		to: "/sco",
		icon: "refresh-ccw",
		category: "site",
		color: "bg-rose-50 text-rose-600 border-rose-200",
		btnText: "View SCOs",
	},

	// Workforce & Muster
	{
		title: "Field Attendance",
		desc: "Daily worker muster, crews & labor attendance",
		to: "/field-attendance",
		icon: "users",
		category: "workforce",
		color: "bg-purple-50 text-purple-600 border-purple-200",
		btnText: "Mark Muster",
	},
	{
		title: "Field Employees",
		desc: "Worker profiles, daily wages & contact details",
		to: "/field-employees",
		icon: "users",
		category: "workforce",
		color: "bg-fuchsia-50 text-fuchsia-600 border-fuchsia-200",
		btnText: "Employees",
	},
	{
		title: "Crews",
		desc: "Sub-contracted & direct labor gang crews",
		to: "/crews",
		icon: "users",
		category: "workforce",
		color: "bg-sky-50 text-sky-600 border-sky-200",
		btnText: "Manage Crews",
	},
	{
		title: "Labour Attendance Register",
		desc: "Daily wage muster calculations & worker logs",
		to: "/labour-attendance",
		icon: "clipboard-list",
		category: "workforce",
		color: "bg-pink-50 text-pink-600 border-pink-200",
		btnText: "Labour Register",
	},

	// Procurement & Inventory
	{
		title: "Material Requests",
		desc: "Raise & track site material requisitions",
		to: "/procurement/material-requests",
		icon: "clipboard-list",
		category: "procurement",
		color: "bg-orange-50 text-orange-600 border-orange-200",
		btnText: "Material Requests",
	},
	{
		title: "Purchase Orders",
		desc: "Issued purchase orders to material suppliers",
		to: "/procurement/purchase-orders",
		icon: "file-text",
		category: "procurement",
		color: "bg-yellow-50 text-yellow-700 border-yellow-200",
		btnText: "Purchase Orders",
	},
	{
		title: "Goods Receipts (GRN)",
		desc: "Confirm site deliveries & physical inspections",
		to: "/procurement/receipts",
		icon: "package",
		category: "procurement",
		color: "bg-emerald-50 text-emerald-600 border-emerald-200",
		btnText: "View Deliveries",
	},
	{
		title: "Material Consumption",
		desc: "Log daily raw materials consumed on site",
		to: "/material-consumption",
		icon: "package",
		category: "procurement",
		color: "bg-cyan-50 text-cyan-600 border-cyan-200",
		btnText: "Log Consumption",
	},
	{
		title: "Items & Inventory",
		desc: "Master catalog of branded construction materials",
		to: "/items",
		icon: "tag",
		category: "procurement",
		color: "bg-blue-50 text-blue-600 border-blue-200",
		btnText: "Items Catalog",
	},

	// Financials & Subcontracting
	{
		title: "Petty Cash & Expenses",
		desc: "Record site petty cash floats & expense claims",
		to: "/project-finance/petty-cash",
		icon: "cash",
		category: "finance",
		color: "bg-slate-50 text-slate-700 border-slate-200",
		btnText: "Manage Cash",
	},
	{
		title: "Subcontractors",
		desc: "Subcontractor directory, contracts & scope",
		to: "/subcontractors",
		icon: "building",
		category: "finance",
		color: "bg-indigo-50 text-indigo-600 border-indigo-200",
		btnText: "Subcontractors",
	},
	{
		title: "Work Orders",
		desc: "Subcontractor work orders & agreed rate schedules",
		to: "/subcontractor-work-orders",
		icon: "file-text",
		category: "finance",
		color: "bg-violet-50 text-violet-600 border-violet-200",
		btnText: "Work Orders",
	},
	{
		title: "Measurement Books (MB)",
		desc: "Record physical site measurements for billing",
		to: "/measurement-books",
		icon: "clipboard-list",
		category: "finance",
		color: "bg-purple-50 text-purple-600 border-purple-200",
		btnText: "Measurement Books",
	},
	{
		title: "Subcontractor Bills",
		desc: "RA bills & subcontractor payment applications",
		to: "/subcontractor-bills",
		icon: "receipt",
		category: "finance",
		color: "bg-emerald-50 text-emerald-600 border-emerald-200",
		btnText: "Subcontract Bills",
	},

	// Estimation & Reports
	{
		title: "Bill of Quantities (BOQ)",
		desc: "Project BOQs, item rates & cost codes",
		to: "/boq",
		icon: "estimation",
		category: "estimation",
		color: "bg-emerald-50 text-emerald-600 border-emerald-200",
		btnText: "View BOQ",
	},
	{
		title: "Construction Rate Master",
		desc: "Standard market rates for labor, material & equipment",
		to: "/rate-master",
		icon: "chart-bar",
		category: "estimation",
		color: "bg-blue-50 text-blue-600 border-blue-200",
		btnText: "Rate Master",
	},
	{
		title: "Assemblies",
		desc: "Composite construction assemblies & rate build-ups",
		to: "/assembly",
		icon: "wrench",
		category: "estimation",
		color: "bg-amber-50 text-amber-600 border-amber-200",
		btnText: "Assemblies",
	},
	{
		title: "Cost vs Budget Report",
		desc: "Planned vs committed vs actual cost variance",
		to: "/reports/cost-vs-budget",
		icon: "chart-bar",
		category: "estimation",
		color: "bg-rose-50 text-rose-600 border-rose-200",
		btnText: "Cost Variance",
	},
];

const filteredModules = computed(() => {
	return allModules.filter((m) => {
		const matchesCategory = selectedCategory.value === "all" || m.category === selectedCategory.value;
		const query = searchQuery.value.toLowerCase().trim();
		const matchesSearch = !query || m.title.toLowerCase().includes(query) || m.desc.toLowerCase().includes(query);
		return matchesCategory && matchesSearch;
	});
});
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
			<div class="flex flex-wrap items-center gap-2.5">
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
					class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-xl shadow-xs transition-all flex items-center gap-2 cursor-pointer"
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
					</svg>
					<span>Site Photos</span>
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

		<!-- Categorized Module Directory Finder -->
		<div>
			<div class="flex flex-wrap items-center justify-between gap-4 mb-4">
				<div>
					<h2 class="text-sm font-bold uppercase tracking-wider text-slate-800">Module Directory & Finder</h2>
					<p class="text-xs text-slate-500 mt-0.5">Filter by category or search any module instantly</p>
				</div>
				<!-- Search Input -->
				<div class="relative w-full sm:w-64">
					<svg class="w-4 h-4 absolute left-3 top-2.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
					</svg>
					<input
						v-model="searchQuery"
						type="text"
						placeholder="Find any module..."
						class="w-full pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-900 focus:ring-2 focus:ring-slate-900 focus:border-slate-900 shadow-xs"
					/>
				</div>
			</div>

			<!-- Category Tabs -->
			<div class="flex items-center gap-2 overflow-x-auto pb-2 mb-4 no-scrollbar">
				<button
					v-for="cat in categories"
					:key="cat.id"
					type="button"
					class="px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer"
					:class="selectedCategory === cat.id ? 'bg-slate-900 text-white shadow-xs' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'"
					@click="selectedCategory = cat.id"
				>
					{{ cat.label }}
				</button>
			</div>

			<!-- Modules Grid -->
			<div v-if="filteredModules.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
				<RouterLink
					v-for="item in filteredModules"
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
								<svg v-else-if="item.icon === 'check-circle'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<svg v-else-if="item.icon === 'calendar'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
								</svg>
								<svg v-else-if="item.icon === 'clipboard-list'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
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

			<!-- Search Empty State -->
			<div v-else class="bg-white border border-slate-200 rounded-2xl p-8 text-center text-slate-500 text-xs my-4">
				No modules found matching "<span class="font-bold text-slate-900">{{ searchQuery }}</span>". Try clearing your search query.
			</div>
		</div>
	</div>
</template>
