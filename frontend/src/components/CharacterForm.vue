<script setup lang="ts">
import { ref, computed } from 'vue'
import { createCharacter as apiCreateCharacter } from '@/api/characters'

const emit = defineEmits<{
  characterCreated: [data: any]
}>()

const characterName = ref('')
const relationship = ref('')
const characterType = ref('person')
const selectedImage = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

const RELATIONSHIPS = [
  { value: 'mother', label: 'Mother' },
  { value: 'father', label: 'Father' },
  { value: 'son', label: 'Son' },
  { value: 'daughter', label: 'Daughter' },
  { value: 'brother', label: 'Brother' },
  { value: 'sister', label: 'Sister' },
  { value: 'grandpa1', label: 'Grandpa 1' },
  { value: 'grandpa2', label: 'Grandpa 2' },
  { value: 'grandma1', label: 'Grandma 1' },
  { value: 'grandma2', label: 'Grandma 2' },
  { value: 'uncle', label: 'Uncle' },
  { value: 'aunt', label: 'Aunt' },
  { value: 'cousin', label: 'Cousin' },
  { value: 'friend', label: 'Friend' },
  { value: 'pet', label: 'Pet' },
  { value: 'other', label: 'Other' },
]

const isValid = computed(() => {
  return characterName.value.trim() && relationship.value && selectedImage.value
})

function handleImageChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    selectedImage.value = file
    previewUrl.value = URL.createObjectURL(file)
    errorMessage.value = null
  }
}

function removeImage() {
  selectedImage.value = null
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
}

async function handleSubmit() {
  if (!isValid.value) return

  isSubmitting.value = true
  errorMessage.value = null

  const formData = new FormData()
  formData.append('name', characterName.value.trim())
  formData.append('relationship', relationship.value)
  formData.append('character_type', characterType.value)
  formData.append('image', selectedImage.value!)

  try {
    const data = await apiCreateCharacter(formData)
    emit('characterCreated', data)
    // Reset form
    characterName.value = ''
    relationship.value = ''
    characterType.value = 'person'
    removeImage()
  } catch (error: any) {
    console.error('Character creation failed:', error)
    errorMessage.value = error?.body?.detail || 'Something went wrong. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="flex flex-col gap-8">

    <!-- Character Name -->
    <div class="flex flex-col gap-2">
      <label class="text-slate-900 dark:text-white text-base font-bold ml-1" for="char-name">Character Name</label>
      <div class="relative group">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-primary transition-colors">
          <span class="material-symbols-outlined">face</span>
        </div>
        <input
          id="char-name"
          v-model="characterName"
          type="text"
          placeholder="e.g. Grandma Rose, Buddy the dog"
          class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white h-14 pl-12 pr-4 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400"
        />
      </div>
    </div>

    <!-- Relationship & Type row -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- Relationship -->
      <div class="flex flex-col gap-2">
        <label class="text-slate-900 dark:text-white text-base font-bold ml-1" for="char-relationship">Relationship</label>
        <div class="relative group">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-primary transition-colors">
            <span class="material-symbols-outlined">family_restroom</span>
          </div>
          <select
            id="char-relationship"
            v-model="relationship"
            class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white h-14 pl-12 pr-4 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all appearance-none"
          >
            <option value="" disabled>Select relationship</option>
            <option v-for="r in RELATIONSHIPS" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
          <div class="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-slate-400">
            <span class="material-symbols-outlined text-lg">expand_more</span>
          </div>
        </div>
      </div>

      <!-- Character Type -->
      <div class="flex flex-col gap-2">
        <span class="text-slate-900 dark:text-white text-base font-bold ml-1">Type</span>
        <div class="grid grid-cols-2 gap-3">
          <label class="cursor-pointer">
            <input v-model="characterType" type="radio" name="charType" value="person" class="peer sr-only" />
            <div class="h-14 flex items-center justify-center gap-2 rounded-xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 peer-checked:border-primary peer-checked:text-primary peer-checked:bg-primary/5 hover:border-primary/50 transition-all font-bold text-sm">
              <span class="material-symbols-outlined text-lg">person</span>
              Person
            </div>
          </label>
          <label class="cursor-pointer">
            <input v-model="characterType" type="radio" name="charType" value="animal" class="peer sr-only" />
            <div class="h-14 flex items-center justify-center gap-2 rounded-xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 peer-checked:border-primary peer-checked:text-primary peer-checked:bg-primary/5 hover:border-primary/50 transition-all font-bold text-sm">
              <span class="material-symbols-outlined text-lg">pets</span>
              Animal
            </div>
          </label>
        </div>
      </div>
    </div>

    <!-- Image Upload -->
    <div class="flex flex-col gap-2">
      <label class="text-slate-900 dark:text-white text-base font-bold ml-1">Upload Photo</label>
      <p class="text-slate-400 dark:text-slate-500 text-xs font-medium ml-1 -mt-1">Upload a photo of a person, family member, or pet. We'll convert it to a sketch for your coloring books.</p>

      <div v-if="!previewUrl" class="relative">
        <label
          for="char-image"
          class="flex flex-col items-center justify-center gap-3 h-48 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-800/50 hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer"
        >
          <div class="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center">
            <span class="material-symbols-outlined text-primary text-2xl">add_photo_alternate</span>
          </div>
          <div class="text-center">
            <span class="text-sm font-bold text-slate-700 dark:text-slate-200">Click to upload</span>
            <p class="text-xs text-slate-400 mt-0.5">JPG, PNG up to 10MB</p>
          </div>
        </label>
        <input id="char-image" type="file" accept="image/*" @change="handleImageChange" class="sr-only" />
      </div>

      <div v-else class="relative rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
        <img :src="previewUrl" alt="Preview" class="w-full h-48 object-contain" />
        <button
          type="button"
          @click="removeImage"
          class="absolute top-3 right-3 w-8 h-8 rounded-full bg-red-500/90 text-white flex items-center justify-center hover:bg-red-600 transition-colors shadow-lg"
        >
          <span class="material-symbols-outlined text-sm">close</span>
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="errorMessage" class="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-center gap-3">
      <span class="material-symbols-outlined text-red-500">error</span>
      <p class="text-sm text-red-600 dark:text-red-400 font-semibold">{{ errorMessage }}</p>
    </div>

    <!-- Submit -->
    <div class="flex flex-col md:flex-row items-center justify-between gap-4 pt-6 border-t border-slate-100 dark:border-slate-800">
      <p class="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-2">
        <span class="material-symbols-outlined text-lg text-primary">info</span>
        The photo will be converted into a sketch-style character.
      </p>
      <button
        type="submit"
        :disabled="!isValid || isSubmitting"
        class="w-full md:w-auto min-w-[220px] h-14 bg-gradient-to-r from-primary to-accent-purple hover:from-primary-dark hover:to-primary active:scale-95 transition-all rounded-full text-white text-base font-bold flex items-center justify-center gap-2 shadow-xl shadow-primary/30 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <template v-if="isSubmitting">
          <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          Processing...
        </template>
        <template v-else>
          <span class="material-symbols-outlined">auto_fix_high</span>
          Create Character
        </template>
      </button>
    </div>
  </form>
</template>
