<script setup>
import { ref, onMounted, computed } from "vue";
import { RouterLink } from "vue-router";
import DeskPage from "@/components/desk/DeskPage.vue";
import DeskSelect from "@/components/desk/DeskSelect.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import UserAvatar from "@/components/UserAvatar.vue";
import { getDailyLogs } from "@/data/dailyLogApi";
import { useDataStore } from "@/stores";

const store = useDataStore();
const logs = ref([]);
const loading = ref(true);
const selectedProject = ref("");

const projects = computed(() => {
	const list = store.projects || [];
	return [
		{ value: "", label: "All Projects" },
		...list.map((p) => ({ value: p.name, label: p.project_name || p.name })),
	];
});

async function fetchLogs() {
	loading.value = true;
	try {
		logs.value = await getDailyLogs({ project: selectedProject.value || undefined });
	} catch (e) {
		console.error("Failed to fetch daily logs", e);
	} finally {
		loading.value = false;
	}
}

onMounted(() => {
	fetchLogs();
});

const weatherIcons = {
	Clear: "☀️",
	Rainy: "🌧️",
	Hot: "🌡️",
	Cold: "❄️",
	Storm: "⛈️",
};
</script>

<template>
	<DeskPage title="Daily Logs" subtitle="Daily site progress, weather conditions, blockers & photo records">
		<template #actions>
			<RouterLink
				to="/daily-logs/new"
				class="inline-flex items-center gap-2 px-3.5 py-2 bg-brand-600 hover:bg-brand-700 active:scale-98 text-white text-xs font-semibold rounded-lg shadow-sm transition-all"
			>
				<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				<span>New Daily Log</span>
			</RouterLink>
		</template>

		<!-- Filters -->
		<div class="mb-6 flex flex-wrap items-center justify-between gap-4 bg-white p-4 border border-ink-200 rounded-xl shadow-xs">
			<div class="w-full sm:w-64">
				<label class="block text-[11px] uppercase tracking-wider font-semibold text-ink-500 mb-1">Filter Project</label>
				<DeskSelect
					v-model="selectedProject"
					:options="projects"
					@change="fetchLogs"
				/>
			</div>
			<div class="text-xs text-ink-500">
				Found <span class="font-bold text-ink-900">{{ logs.length }}</span> daily log entry record{{ logs.length === 1 ? '' : 's' }}
			</div>
		</div>

		<!-- Skeleton loading -->
		<div v-if="loading" class="space-y-4">
			<div v-for="n in 4" :key="n" class="animate-pulse bg-ink-100 rounded-xl h-36"></div>
		</div>

		<!-- Log Entries List -->
		<div v-else-if="logs.length" class="space-y-4">
			<div
				v-for="log in logs"
				:key="log.name"
				class="bg-white border border-ink-200 rounded-xl p-5 shadow-xs hover:shadow-md transition-all duration-200"
			>
				<div class="flex flex-wrap items-start justify-between gap-3 mb-3 pb-3 border-b border-ink-100">
					<div>
						<div class="flex items-center gap-2">
							<span class="text-base font-bold text-ink-900">{{ log.project_name || log.project }}</span>
							<span
								v-if="log.blocker_flag"
								class="px-2 py-0.5 text-[10px] uppercase font-bold text-danger-700 bg-danger-50 border border-danger-200 rounded-full inline-flex items-center gap-1"
							>
								🚨 Blocker Reported
							</span>
						</div>
						<div class="text-xs text-ink-500 mt-1 flex items-center gap-3">
							<span class="font-mono text-ink-700 font-medium">{{ log.entry_date }}</span>
							<span>·</span>
							<span class="flex items-center gap-1">
								<span>{{ weatherIcons[log.weather_condition] || "🌤️" }}</span>
								<span>{{ log.weather_condition || "Clear" }}</span>
							</span>
							<span>·</span>
							<span>By {{ log.author_name }}</span>
						</div>
					</div>
					<div class="text-right">
						<span class="text-xl font-bold text-brand-700 font-mono">{{ log.progress_percentage || 0 }}%</span>
						<div class="text-[10px] uppercase tracking-wider text-ink-400 font-semibold">Progress</div>
					</div>
				</div>

				<!-- Narrative -->
				<p class="text-xs text-ink-700 leading-relaxed mb-4 whitespace-pre-line">
					{{ log.narrative_description || "No narrative entered for this daily log." }}
				</p>

				<!-- Blocker Warning Details -->
				<div v-if="log.blocker_flag && log.blocker_details" class="mb-4 p-3 bg-danger-50 border border-danger-200 rounded-lg text-xs text-danger-900">
					<div class="font-bold mb-0.5 flex items-center gap-1">
						<span>⚠️ Blocker Description</span>
					</div>
					<div>{{ log.blocker_details }}</div>
				</div>

				<!-- Attached Site Photos -->
				<div v-if="log.photos && log.photos.length" class="mt-3">
					<div class="text-[11px] uppercase tracking-wider font-semibold text-ink-500 mb-2">Attached Site Photos</div>
					<div class="flex flex-wrap gap-2">
						<a
							v-for="photo in log.photos"
							:key="photo.name"
							:href="photo.file_url"
							target="_blank"
							class="w-16 h-16 rounded-lg overflow-hidden border border-ink-200 hover:border-brand-500 transition-colors group shrink-0"
						>
							<img :src="photo.file_url" :alt="photo.file_name" class="w-full h-full object-cover group-hover:scale-110 transition-transform" />
						</a>
					</div>
				</div>
			</div>
		</div>

		<!-- Empty state -->
		<div v-else class="bg-white border border-ink-200 rounded-xl p-12 text-center my-6 max-w-md mx-auto">
			<div class="w-16 h-16 rounded-full bg-brand-50 text-brand-600 mx-auto flex items-center justify-center mb-4">
				<svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
				</svg>
			</div>
			<h3 class="text-base font-semibold text-ink-900 mb-1">No daily logs recorded</h3>
			<p class="text-xs text-ink-500 mb-5">Create your site engineer daily log to track progress, weather, and site blockers.</p>
			<RouterLink
				to="/daily-logs/new"
				class="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded-lg shadow-sm"
			>
				File Daily Log
			</RouterLink>
		</div>
	</DeskPage>
</template>
