<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'

const galleryItems = [
  {
    title: "Aidan's Safari Adventure",
    author: "DadOfThree",
    likes: 245,
    liked: true,
    pages: 12,
    tags: ["Animals", "Toddler"],
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuAtpXmU4qJb2lqkbXvcNTY8pqm3ZcLPuALJyAcGxALZWQeQmJ5HNKO4kNNX01L1OPS04pV6Jdin9iSynUxreyaaaQLQF3J2DDC5BjD23d8J0V4ofOLO09miVS730n0EovR2xxjkNlrPeHbXL6xsS-hIE0xz1Da9E-bP-XYHCvPVAYXsOTz2wQbo1_Xn_fqDtOumM_OyLLLIWW-1j9k7fNRBVGAJSGrQp16T5cHKy9omWYaYr6KwTHr6KJTauAjVwwwF_TH-Y6KVctJ5",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuCyZWklZRzGOIi7iHHPPnHyynN9JQxid0UsuiVIKQoyQ0xdvtNp9aOvtSfAxnIMLUuig60SOt2yMJtfjn9Si6rYXKu4CO78xcVpNzjThBiuAjbMgKHJ3zUuSchxKl6JgzCMJRPRnqPIE4hpz_EGAXINQ8WGTGCsHGzFFUWHwpKSVZUNo7UQCAJNfbUB7OQjvf4ltgs1uQTBH4v0tHdTBd2qm5U7khQmpjmfIxmqlNWEGc0AEYTtLWduxptu9gL0WikbhoYmBf0A-asq",
  },
  {
    title: "Mia's Space Journey",
    author: "MamaMia",
    likes: 189,
    liked: false,
    pages: 0,
    tags: ["Space", "Sci-Fi"],
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuAPxlEXtdVD5Ztu_KNdg_iTAIDQFye6kT78M1V0Sq5FcSByykGeihHQXP7bVgURiVkvAS_BCEjzQMcLuks6qPGh3gnQu41y-ZE75axa7-G1hT721wqgwFLYgc4NkIZ7UtFbfu3XfTEklgbVLwUdc-1rR3BrpyJAvnnexTovO9sexO-LKfBk9oTuCaMm7efaS1z2TYCj28Dq7WTEVuLzhStNFHlv8TAcFZNuBR-9YPuwaJq3dG1aLqseWZrWK0vMUlUzOqV4WCnrpqHF",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuBr4snMVRHdurgkob2jGH9TdORR5UJiTqJYt8RitJ8K02fQfGyjfxyywQ94czz4DivAyCwiB_E4HdZuDywxfAXRUtaUvDypDyMh6bEe5IEfMRDJarFjecgGIO3QAjYldzyu8UNajI07-SmR8luHttETGPPoKBow7EpvATHc-HPxfJLqqlBzAxINm7n91xYT-XJLKcErLTC3qO_dnZjeWp103pfQuoY3WJJlOkxFjT112uvZNG4U3EuVmVLMSng0srvB1GJzPvCp2I2w",
  },
  {
    title: "Leo the Dragon Tamer",
    author: "LeoCreates",
    likes: 312,
    liked: true,
    pages: 0,
    tags: ["Fantasy", "Dragons"],
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuDiDjXktnnsjd4LXaKw0EHL8-uL4gLD8VYs7Sl3mMzNd-YwpUjGrRIpifWRLsExii-8UiOSJqVLdhd5Bp8O0ElDKebAY3ZiW1MsrwamS4cJSZArZhtYrWzdGolMhZ1Sgfkrx-PFrOo47EpxRHcfvfw0tEP8wjr-HTNnnrorq-trrX3-DZcQOoWQazNL8uqArXiTylBRT0M8ZAKX1vc69AgKJyLmnf1MFuYu4Ds_Mt90wfNMgF2CyUZnJAlSF9yAeb25vibq3OzRPdUy",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuBWI6gnlsHUSNOUZ-zcw00oilsxw-IrUD-4GEE1eNM2kRcyuNGY5GqlOKaitmd4hAc-X9hkUO_oAY5vbfekqEDbvOyX8G2WjVcNrMvkHSubEbbXgqOULjdd6AoTN4pewoGj3GJ84cvdEmqXNRrEASvpOjW2DR8YGTJocDyWgCUc2eF7pr1Ich67tf00qgUq-RjN6JhEhv7EGw9OrQLd-foafBrdyJrhXY2HYO42uoMgAjkn9JXmaZbfngZru9_xMBgMxW9nK0jIsN32",
  },
  {
    title: "Sophie's Princess Castle",
    author: "SophieMom",
    likes: 156,
    liked: false,
    pages: 0,
    tags: ["Fantasy", "Princess"],
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuDhT_Uyo14FAEozPZriCMlMB5JmifGWUW6JD_e5bg2kUZEQ0Xk47aaF8k0qcjepkXfU9CGFs7De4l2VjjyndijOplq8GW_sAHk5mwBDhbDaoHzEgiymlZdrQtzEUVIKHO4DLBMei1E6iJp5XnW9MMhkg8eiyX4TzbGflnEAOSHPst8aFX2KCOprQ_3JXdsEDGzq8295E3cGXcrJMPqfAegkVAs1fG5_LPsNigSwspiARVn-ae0qR0S72oE06JHDUwJT5ZHFupnNjUQg",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuA9z9cWpg4NhDXaT2v3EeR0g-ggyr7F8O5wbErH2zEc-UklvoyNlbK6j7xXDr9oiDH5ZwjvbXpJEEKFvF1FEKa3MBHIF1mGmjTqKibgPCfZmtZbxfMOor3_lvFgmsbDp8Bgn8NJ6fPTl9DmUaQDvJ-J6urz0OerY0rP4U-kd3OPndROqbvhGIXY6MgmRlo6slQnPmErgjtvCH8LcSKqNz_x9tMDyXyg-FgcFI4lATcPCFvRRrROAQluXtzsXFNe7E8HwRshY03Mq-NK",
  },
  {
    title: "Ben's Dinosaur World",
    author: "BenjiRex",
    likes: 402,
    liked: true,
    pages: 0,
    tags: ["Animals", "Dino"],
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuC_0Xq-CB8n44eofTSZswAy73oJsBUsKe7O31g-dDCFopw5eP9qqt4o1Mm4fjDPJ-Qg7I8oAYkjN6E1a-JDQC2FV5JXcjBZ1NY1pNSCTDauc8OR_84o8yo0KZRSMQLkdq3qKLzDTpMGW81RNWsAXBECqnmhZIjKmhHzik2mEieruOF-d7E0sPeTFJhM73TRfeZ62w5HQjlnayrSTEwpQGKR9l5YzNNTF9avofzTcqlQWKfOxo1ogQzYsYBMGk07hax834ftoqdlWPRI",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuBtMhZc2NmDHx6lhFSxmpuYe1m2ctUgkCFC0B6rwiG-USPAwAhzdW07S_fqREtPyY0EpAkqNE5GbgYSLO_D1Watp36M3u6kEdqZDnS2tbZ-x2wJlRCByASIMYiDi1I9yyy0Hp1S8RNB8xop4NunAcDQFgjyWZyN_Qt3qxNkWeW4isNr2MoLcSYqfhZYfJ68lWLbP9hlMhWkn2e9FNwWiBdHnVyzB-ZO2zJqz_UGcApWypVQdNlFdJxo0_gYuzmwljaHEn7IlbgTbRk7",
  },
  {
    title: "Emma's Underwater Party",
    author: "EmmaArt",
    likes: 120,
    liked: false,
    pages: 20,
    tags: ["Ocean", "Fish"],
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuBf-M5u5AOSmC1gDmM3bV0A3chzek6HtjXXN6GSX_2x0VqJByBX6WlHCHHHWxowA7ZjvuRvdfr62_FVHqrGaWit2XoQr59ICRU2qMkZsNEpWDyBFv6uJztg49o9QTIr3m6eeMy7_FxFxtlEGowg49QuH-p1mzV42UgXB_F-WVBZzMkfQ-rWA2BfqFS9JFpRStDn6aAylluP7jVhjqPQTjvi5R_zrs_jA2xiposPOFFJ-Y8PvfFck-W2Ftm902Kf5ohJYc_rb5HlRLgj",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDaYBjC_K-jgU1AJ8ttfjCzX8eb21JsAHQDImCzlAAif8Sf36EmY_90jfSQd9lcGcYr34OWj9_ooyijFjySvlxQPPVECSavk-hS3lcKkWdorXg8tAj81yxF4gzsYv_Lw9KCeFhQxWDukM-XPl566tw2EkEZlg8lzUZ2WlkVU23wY5h-UuIbSnQnQNCcXCMsklM4hjqoSMWnm5DZk4kOxahXm5O9mmN_C9a7TYo4Y3vNMTi885PSV1JmsjvM63PYmF7O9Age4FBXouG1",
  },
]

const filters = [
  { label: "Most Popular", icon: "local_fire_department", active: true },
  { label: "Most Recent", icon: "schedule", active: false },
]

const themeFilters = [
  { label: "Animals", icon: "pets" },
  { label: "Space", icon: "rocket_launch" },
  { label: "Fantasy", icon: "auto_fix_high" },
  { label: "Superheroes", icon: "sentiment_satisfied" },
]
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 flex flex-col p-6 md:p-10 gap-8 w-full max-w-7xl mx-auto">
      <!-- Hero Section -->
      <div class="flex flex-col gap-3">
        <h1 class="text-slate-900 dark:text-white text-4xl md:text-5xl font-extrabold leading-tight tracking-tight">Community Inspiration</h1>
        <p class="text-slate-500 dark:text-slate-400 text-lg md:text-xl font-medium max-w-2xl">Discover amazing coloring books created by our community. Remix any design to start your own masterpiece.</p>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap items-center gap-3">
        <button
          v-for="filter in filters"
          :key="filter.label"
          class="flex h-10 items-center justify-center gap-2 rounded-full px-5 transition-all"
          :class="filter.active
            ? 'bg-primary text-white shadow-lg shadow-primary/20 hover:bg-primary/90'
            : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-primary/50 hover:text-primary'"
        >
          <span class="material-symbols-outlined text-[20px]">{{ filter.icon }}</span>
          <span class="text-sm font-bold">{{ filter.label }}</span>
        </button>

        <div class="w-px h-6 bg-slate-300 dark:bg-slate-700 mx-1 hidden sm:block"></div>

        <button
          v-for="theme in themeFilters"
          :key="theme.label"
          class="flex h-10 items-center justify-center gap-2 rounded-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 px-5 text-slate-600 dark:text-slate-300 hover:border-primary/50 hover:text-primary transition-all"
        >
          <span class="material-symbols-outlined text-[20px]">{{ theme.icon }}</span>
          <span class="text-sm font-medium">{{ theme.label }}</span>
        </button>
      </div>

      <!-- Gallery Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="item in galleryItems"
          :key="item.title"
          class="group relative flex flex-col gap-3 bg-white dark:bg-slate-900 p-3 rounded-2xl shadow-sm hover:shadow-xl hover:shadow-primary/5 border border-transparent hover:border-primary/20 transition-all duration-300"
        >
          <div class="relative w-full aspect-[3/4] overflow-hidden rounded-xl">
            <img :src="item.image" :alt="item.title" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center p-4">
              <button class="bg-primary hover:bg-primary/90 text-white font-bold py-2.5 px-6 rounded-full shadow-lg transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300 flex items-center gap-2">
                <span class="material-symbols-outlined text-[18px]">cached</span>
                Remix Theme
              </button>
            </div>
            <div v-if="item.pages" class="absolute top-3 right-3 bg-black/40 backdrop-blur-md text-white text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1">
              <span class="material-symbols-outlined text-[14px]">photo_library</span> {{ item.pages }} Pages
            </div>
          </div>
          <div class="px-1 pb-1">
            <h3 class="text-slate-900 dark:text-white text-lg font-bold leading-tight line-clamp-1">{{ item.title }}</h3>
            <div class="flex items-center justify-between mt-2">
              <div class="flex items-center gap-2">
                <img :src="item.avatar" :alt="item.author" class="size-6 rounded-full object-cover" />
                <span class="text-xs text-slate-500 font-medium">by {{ item.author }}</span>
              </div>
              <div class="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
                <span
                  class="material-symbols-outlined text-[18px] cursor-pointer transition-colors"
                  :class="item.liked ? 'text-red-500' : 'hover:text-red-500'"
                  :style="item.liked ? 'font-variation-settings: \'FILL\' 1;' : ''"
                >favorite</span>
                <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">{{ item.likes }}</span>
              </div>
            </div>
            <div class="mt-3 flex gap-2">
              <span
                v-for="tag in item.tags"
                :key="tag"
                class="bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wide"
              >{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div class="flex justify-center mt-8">
        <button class="flex items-center gap-2 px-8 py-3 rounded-full border border-slate-200 dark:border-slate-700 hover:border-primary/50 text-slate-600 dark:text-slate-300 hover:text-primary font-bold transition-all bg-white dark:bg-slate-900">
          <span>Load More Inspiration</span>
          <span class="material-symbols-outlined">expand_more</span>
        </button>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
