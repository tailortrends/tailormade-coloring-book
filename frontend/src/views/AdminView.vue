<script setup lang="ts">
import { ref, onMounted, onUnmounted, shallowRef } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import {
  getAdminStats,
  getDailyAnalytics,
  getFailures,
  getCosts,
  getStripeMode,
  setStripeMode,
  type AdminStats,
  type DailyAnalytics,
  type FailedBook,
  type CostEntry,
} from '@/api/admin'
import {
  Chart,
  LineController,
  BarController,
  DoughnutController,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

Chart.register(
  LineController,
  BarController,
  DoughnutController,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler,
)

const isLoading = ref(true)
const stats = ref<AdminStats | null>(null)
const daily = ref<DailyAnalytics[]>([])
const failures = ref<FailedBook[]>([])
const costEntries = ref<CostEntry[]>([])

// Stripe mode toggle
const stripeMode = ref<'test' | 'live'>('test')
const stripeModeLoading = ref(false)

async function toggleStripeMode() {
  const newMode = stripeMode.value === 'test' ? 'live' : 'test'
  if (newMode === 'live' && !confirm('Switch to LIVE Stripe mode? Real charges will be processed.')) {
    return
  }
  stripeModeLoading.value = true
  try {
    const result = await setStripeMode(newMode)
    stripeMode.value = result.mode as 'test' | 'live'
  } catch (e) {
    console.error('Failed to toggle stripe mode', e)
  } finally {
    stripeModeLoading.value = false
  }
}

// Chart refs
const booksChartCanvas = ref<HTMLCanvasElement | null>(null)
const costChartCanvas = ref<HTMLCanvasElement | null>(null)
const themesChartCanvas = ref<HTMLCanvasElement | null>(null)
const tierChartCanvas = ref<HTMLCanvasElement | null>(null)
const chartInstances = shallowRef<Chart[]>([])

function formatCost(value: number): string {
  return `$${value.toFixed(4)}`
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

function destroyCharts() {
  for (const chart of chartInstances.value) {
    chart.destroy()
  }
  chartInstances.value = []
}

function renderCharts() {
  destroyCharts()
  const instances: Chart[] = []

  // Sort daily data chronologically (oldest first)
  const sorted = [...daily.value].sort((a, b) => a.date.localeCompare(b.date))
  const labels = sorted.map(d => formatDate(d.date))

  // Books per day line chart
  if (booksChartCanvas.value) {
    instances.push(
      new Chart(booksChartCanvas.value, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'Books Generated',
              data: sorted.map(d => d.books_generated ?? 0),
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59,130,246,0.1)',
              fill: true,
              tension: 0.3,
            },
            {
              label: 'Failures',
              data: sorted.map(d => d.failures ?? 0),
              borderColor: '#ef4444',
              backgroundColor: 'rgba(239,68,68,0.1)',
              fill: true,
              tension: 0.3,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } },
        },
      }),
    )
  }

  // Cost per day line chart
  if (costChartCanvas.value) {
    instances.push(
      new Chart(costChartCanvas.value, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'Daily Cost ($)',
              data: sorted.map(d => d.total_cost ?? 0),
              borderColor: '#10b981',
              backgroundColor: 'rgba(16,185,129,0.1)',
              fill: true,
              tension: 0.3,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } },
        },
      }),
    )
  }

  // Top themes horizontal bar chart
  if (themesChartCanvas.value && stats.value?.top_themes?.length) {
    const themeColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    instances.push(
      new Chart(themesChartCanvas.value, {
        type: 'bar',
        data: {
          labels: stats.value.top_themes.map(t => t.theme),
          datasets: [
            {
              label: 'Books',
              data: stats.value.top_themes.map(t => t.count),
              backgroundColor: stats.value.top_themes.map((_, i) => themeColors[i % themeColors.length]),
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: { legend: { display: false } },
        },
      }),
    )
  }

  // Tier donut chart
  if (tierChartCanvas.value && stats.value?.books_by_tier) {
    const tierLabels = Object.keys(stats.value.books_by_tier)
    const tierData = Object.values(stats.value.books_by_tier)
    const tierColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    instances.push(
      new Chart(tierChartCanvas.value, {
        type: 'doughnut',
        data: {
          labels: tierLabels,
          datasets: [
            {
              data: tierData,
              backgroundColor: tierLabels.map((_, i) => tierColors[i % tierColors.length]),
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } },
        },
      }),
    )
  }

  chartInstances.value = instances
}

onMounted(async () => {
  try {
    const [s, d, f, c, sm] = await Promise.all([
      getAdminStats(),
      getDailyAnalytics(30),
      getFailures(20),
      getCosts(50),
      getStripeMode().catch(() => ({ mode: 'test' })),
    ])
    stats.value = s
    daily.value = d
    failures.value = f
    costEntries.value = c
    stripeMode.value = sm.mode as 'test' | 'live'

    // Render charts after data loaded (nextTick ensures canvas is mounted)
    requestAnimationFrame(renderCharts)
  } catch (e) {
    console.error('Failed to load admin data', e)
  } finally {
    isLoading.value = false
  }
})

onUnmounted(destroyCharts)
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 py-8 px-4 sm:px-8 max-w-7xl mx-auto w-full">
      <div class="flex items-center justify-between gap-3 mb-8">
        <div class="flex items-center gap-3">
          <div class="size-10 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center text-red-600 dark:text-red-400">
            <span class="material-symbols-outlined">admin_panel_settings</span>
          </div>
          <div>
            <h1 class="text-3xl font-extrabold tracking-tight">Admin Dashboard</h1>
            <p class="text-sm text-slate-500 dark:text-slate-400">Internal analytics &amp; cost tracking</p>
          </div>
        </div>

        <!-- Stripe Mode Toggle -->
        <div class="flex items-center gap-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 px-4 py-3">
          <span class="material-symbols-outlined text-lg" :class="stripeMode === 'live' ? 'text-green-500' : 'text-amber-500'">
            {{ stripeMode === 'live' ? 'verified' : 'science' }}
          </span>
          <div class="flex flex-col">
            <span class="text-xs font-bold uppercase tracking-wider" :class="stripeMode === 'live' ? 'text-green-600 dark:text-green-400' : 'text-amber-600 dark:text-amber-400'">
              Stripe {{ stripeMode }}
            </span>
            <span class="text-[10px] text-slate-400">{{ stripeMode === 'live' ? 'Real charges' : 'No charges' }}</span>
          </div>
          <button
            @click="toggleStripeMode"
            :disabled="stripeModeLoading"
            class="relative ml-2 w-12 h-6 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50"
            :class="stripeMode === 'live' ? 'bg-green-500 focus:ring-green-500' : 'bg-slate-300 dark:bg-slate-600 focus:ring-amber-500'"
          >
            <span
              class="absolute top-0.5 left-0.5 size-5 bg-white rounded-full shadow transition-transform duration-200"
              :class="stripeMode === 'live' ? 'translate-x-6' : 'translate-x-0'"
            />
          </button>
        </div>
      </div>

      <!-- Loading skeleton -->
      <div v-if="isLoading" class="space-y-6">
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <div v-for="i in 5" :key="i" class="h-24 rounded-xl bg-slate-200 dark:bg-slate-700 animate-pulse" />
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-for="i in 4" :key="i" class="h-64 rounded-xl bg-slate-200 dark:bg-slate-700 animate-pulse" />
        </div>
      </div>

      <template v-else-if="stats">
        <!-- Summary Cards -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Total Books</p>
            <p class="text-2xl font-bold mt-1">{{ stats.total_books }}</p>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">This Month</p>
            <p class="text-2xl font-bold mt-1">{{ stats.books_this_month }}</p>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Total Cost</p>
            <p class="text-2xl font-bold mt-1">{{ formatCost(stats.total_spend) }}</p>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Avg Cost/Book</p>
            <p class="text-2xl font-bold mt-1">{{ formatCost(stats.avg_cost_per_book) }}</p>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Library Hit Rate</p>
            <p class="text-2xl font-bold mt-1">{{ stats.library_hit_rate }}%</p>
          </div>
        </div>

        <!-- Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Books per Day (last 30 days)</h3>
            <div class="h-64"><canvas ref="booksChartCanvas" /></div>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Cost per Day (last 30 days)</h3>
            <div class="h-64"><canvas ref="costChartCanvas" /></div>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Top Themes</h3>
            <div class="h-64"><canvas ref="themesChartCanvas" /></div>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Books by Tier</h3>
            <div class="h-64"><canvas ref="tierChartCanvas" /></div>
          </div>
        </div>

        <!-- Recent Failures Table -->
        <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 mb-8">
          <div class="p-4 border-b border-slate-200 dark:border-slate-700">
            <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200">Recent Failures</h3>
          </div>
          <div v-if="failures.length === 0" class="p-8 text-center text-slate-400">
            No failures recorded.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-slate-50 dark:bg-slate-700/50">
                <tr>
                  <th class="px-4 py-2 text-left font-semibold text-slate-600 dark:text-slate-300">Book ID</th>
                  <th class="px-4 py-2 text-left font-semibold text-slate-600 dark:text-slate-300">UID</th>
                  <th class="px-4 py-2 text-left font-semibold text-slate-600 dark:text-slate-300">Theme</th>
                  <th class="px-4 py-2 text-left font-semibold text-slate-600 dark:text-slate-300">Error</th>
                  <th class="px-4 py-2 text-left font-semibold text-slate-600 dark:text-slate-300">Time</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
                <tr v-for="f in failures" :key="f.book_id" class="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                  <td class="px-4 py-2 font-mono text-xs truncate max-w-[120px]">{{ f.book_id }}</td>
                  <td class="px-4 py-2 font-mono text-xs truncate max-w-[100px]">{{ f.uid }}</td>
                  <td class="px-4 py-2 capitalize">{{ f.theme }}</td>
                  <td class="px-4 py-2 text-red-600 dark:text-red-400 truncate max-w-[250px]">{{ f.error }}</td>
                  <td class="px-4 py-2 text-slate-500 whitespace-nowrap">{{ formatDate(f.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Most Expensive Books Table -->
        <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <div class="p-4 border-b border-slate-200 dark:border-slate-700">
            <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200">Most Expensive Books</h3>
          </div>
          <div v-if="costEntries.length === 0" class="p-8 text-center text-slate-400">
            No cost records yet.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-slate-50 dark:bg-slate-700/50">
                <tr>
                  <th class="px-4 py-2 text-left font-semibold text-slate-600 dark:text-slate-300">Book ID</th>
                  <th class="px-4 py-2 text-left font-semibold text-slate-600 dark:text-slate-300">Theme</th>
                  <th class="px-4 py-2 text-right font-semibold text-slate-600 dark:text-slate-300">Total Cost</th>
                  <th class="px-4 py-2 text-right font-semibold text-slate-600 dark:text-slate-300">Lib Hits</th>
                  <th class="px-4 py-2 text-right font-semibold text-slate-600 dark:text-slate-300">Lib Misses</th>
                  <th class="px-4 py-2 text-right font-semibold text-slate-600 dark:text-slate-300">Retries</th>
                  <th class="px-4 py-2 text-left font-semibold text-slate-600 dark:text-slate-300">Time</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
                <tr v-for="c in costEntries" :key="c.book_id" class="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                  <td class="px-4 py-2 font-mono text-xs truncate max-w-[120px]">{{ c.book_id }}</td>
                  <td class="px-4 py-2 capitalize">{{ c.theme }}</td>
                  <td class="px-4 py-2 text-right font-semibold">{{ formatCost(c.total_cost) }}</td>
                  <td class="px-4 py-2 text-right text-emerald-600">{{ c.library_hits }}</td>
                  <td class="px-4 py-2 text-right text-amber-600">{{ c.library_misses }}</td>
                  <td class="px-4 py-2 text-right">{{ c.retry_count }}</td>
                  <td class="px-4 py-2 text-slate-500 whitespace-nowrap">{{ formatDate(c.timestamp) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>
