import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as profilesApi from '@/api/profiles'
import type { Profile, ProfileCreate, ProfileUpdate } from '@/api/profiles'

const ACTIVE_PROFILE_KEY = 'tailormade_active_profile_id'

export const useProfilesStore = defineStore('profiles', () => {
  const profiles = ref<Profile[]>([])
  const activeProfileId = ref<string | null>(localStorage.getItem(ACTIVE_PROFILE_KEY))
  const isLoading = ref(false)

  const activeProfile = computed(() => {
    if (!activeProfileId.value) return null
    return profiles.value.find(p => p.profile_id === activeProfileId.value) ?? null
  })

  const hasProfiles = computed(() => profiles.value.length > 0)

  function setActiveProfile(profileId: string) {
    activeProfileId.value = profileId
    localStorage.setItem(ACTIVE_PROFILE_KEY, profileId)
  }

  function clearActiveProfile() {
    activeProfileId.value = null
    localStorage.removeItem(ACTIVE_PROFILE_KEY)
  }

  async function fetchProfiles() {
    isLoading.value = true
    try {
      profiles.value = await profilesApi.listProfiles()

      // If we have a stored activeProfileId, verify it still exists
      if (activeProfileId.value) {
        const stillExists = profiles.value.some(p => p.profile_id === activeProfileId.value)
        if (!stillExists) {
          // Fall back to the default profile
          const defaultProfile = profiles.value.find(p => p.is_default)
          if (defaultProfile) {
            setActiveProfile(defaultProfile.profile_id)
          } else if (profiles.value.length > 0) {
            setActiveProfile(profiles.value[0]!.profile_id)
          } else {
            clearActiveProfile()
          }
        }
      } else {
        // No stored active — use the default
        const defaultProfile = profiles.value.find(p => p.is_default)
        if (defaultProfile) {
          setActiveProfile(defaultProfile.profile_id)
        } else if (profiles.value.length > 0) {
          setActiveProfile(profiles.value[0]!.profile_id)
        }
      }
    } catch (e) {
      console.error('Failed to fetch profiles', e)
    } finally {
      isLoading.value = false
    }
  }

  async function createProfile(data: ProfileCreate): Promise<Profile> {
    const profile = await profilesApi.createProfile(data)
    profiles.value.push(profile)
    // If it's the first/default profile, make it active
    if (profile.is_default || profiles.value.length === 1) {
      setActiveProfile(profile.profile_id)
    }
    return profile
  }

  async function updateProfile(profileId: string, data: ProfileUpdate): Promise<Profile> {
    const updated = await profilesApi.updateProfile(profileId, data)
    const idx = profiles.value.findIndex(p => p.profile_id === profileId)
    if (idx !== -1) {
      profiles.value[idx] = updated
    }
    return updated
  }

  async function deleteProfile(profileId: string) {
    await profilesApi.deleteProfile(profileId)
    profiles.value = profiles.value.filter(p => p.profile_id !== profileId)

    // If we deleted the active profile, switch to default
    if (activeProfileId.value === profileId) {
      const defaultProfile = profiles.value.find(p => p.is_default)
      if (defaultProfile) {
        setActiveProfile(defaultProfile.profile_id)
      } else if (profiles.value.length > 0) {
        setActiveProfile(profiles.value[0]!.profile_id)
      } else {
        clearActiveProfile()
      }
    }
  }

  async function setDefault(profileId: string) {
    const updated = await profilesApi.setDefaultProfile(profileId)
    // Mark all as non-default, then set the one
    profiles.value.forEach(p => { p.is_default = false })
    const idx = profiles.value.findIndex(p => p.profile_id === profileId)
    if (idx !== -1) {
      profiles.value[idx] = updated
    }
    setActiveProfile(profileId)
  }

  return {
    profiles,
    activeProfileId,
    activeProfile,
    hasProfiles,
    isLoading,
    fetchProfiles,
    createProfile,
    updateProfile,
    deleteProfile,
    setDefault,
    setActiveProfile,
    clearActiveProfile,
  }
})
