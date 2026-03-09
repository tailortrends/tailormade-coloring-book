import { ref, computed } from 'vue'
import type { ZodSchema, ZodError } from 'zod'

/**
 * Reusable composable for Zod-based form validation.
 *
 * Usage:
 *   const { errors, validate, validateField, isValid, clearErrors } = useFormValidation(schema)
 *   const ok = validate({ title, theme, ... })
 *   // or on blur:
 *   validateField('title', title.value)
 */
export function useFormValidation<T extends Record<string, unknown>>(schema: ZodSchema<T>) {
  const errors = ref<Partial<Record<keyof T, string>>>({})

  const isValid = computed(() => Object.keys(errors.value).length === 0)

  /** Validate the entire form. Returns true if valid. */
  function validate(data: unknown): data is T {
    const result = schema.safeParse(data)
    if (result.success) {
      errors.value = {}
      return true
    }
    errors.value = formatErrors(result.error)
    return false
  }

  /** Validate a single field (useful for on-blur). */
  function validateField(field: keyof T, value: unknown) {
    // Build a partial object and validate just this field via the full schema
    // We use `pick` if available, but safest to just parse and extract
    const partial = { [field]: value } as unknown
    const result = schema.safeParse(partial)

    if (result.success) {
      const next = { ...errors.value }
      delete next[field]
      errors.value = next
    } else {
      const fieldErrors = result.error.issues
        .filter((i) => i.path[0] === field)
        .map((i) => i.message)
      if (fieldErrors.length) {
        errors.value = { ...errors.value, [field]: fieldErrors[0] }
      } else {
        const next = { ...errors.value }
        delete next[field]
        errors.value = next
      }
    }
  }

  function clearErrors() {
    errors.value = {}
  }

  function formatErrors(error: ZodError): Partial<Record<keyof T, string>> {
    const result: Partial<Record<string, string>> = {}
    for (const issue of error.issues) {
      const key = issue.path[0] as string
      if (key && !result[key]) {
        result[key] = issue.message
      }
    }
    return result as Partial<Record<keyof T, string>>
  }

  return { errors, isValid, validate, validateField, clearErrors }
}
