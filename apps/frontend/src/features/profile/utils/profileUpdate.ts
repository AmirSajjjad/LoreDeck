import type { Profile, ProfileFormValues, ProfileUpdateRequest } from '@/features/profile/types'

type NullableEditableField = 'phone_number' | 'profile_pic' | 'name' | 'email'

const nullableEditableFields: readonly NullableEditableField[] = [
  'phone_number',
  'profile_pic',
  'name',
  'email',
]

export function profileToFormValues(profile: Profile): ProfileFormValues {
  return {
    username: profile.username,
    phone_number: profile.phone_number ?? '',
    profile_pic: profile.profile_pic ?? '',
    name: profile.name ?? '',
    email: profile.email ?? '',
  }
}

export function createProfileUpdate(
  values: ProfileFormValues,
  current: Profile,
): ProfileUpdateRequest {
  const update: ProfileUpdateRequest = {}
  if (values.username !== current.username) update.username = values.username

  for (const field of nullableEditableFields) {
    const value = values[field] === '' ? null : values[field]
    if (value !== current[field]) update[field] = value
  }

  return update
}
