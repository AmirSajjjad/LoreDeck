import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import BaseInput from '@/components/common/BaseInput.vue'
import ProfileEditForm from '@/features/profile/components/ProfileEditForm.vue'

const profile = {
  id: 1,
  username: 'sara',
  phone_number: null,
  profile_pic: null,
  name: 'سارا',
  email: 'sara@example.test',
  telegram_id: null,
  created_at: '2026-01-01T00:00:00Z',
}

describe('validated forms', () => {
  it('announces Persian required-field errors', async () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: 'required-field',
        name: 'required-field',
        label: 'نام کاربری',
        modelValue: '',
        required: true,
        error: 'وارد کردن این فیلد الزامی است.',
      },
    })
    expect(wrapper.text()).toContain('وارد کردن این فیلد الزامی است.')
    expect(wrapper.get('input').attributes('aria-invalid')).toBe('true')
    expect(wrapper.get('[role="alert"]').attributes('id')).toBe('required-field-error')
  })

  it('preserves useForm initial values when validated controls have no v-model', async () => {
    const wrapper = mount(ProfileEditForm, { props: { profile } })
    await flushPromises()
    expect((wrapper.get('#profile-username').element as HTMLInputElement).value).toBe('sara')
    expect((wrapper.get('#profile-name').element as HTMLInputElement).value).toBe('سارا')
    expect((wrapper.get('#profile-email').element as HTMLInputElement).value).toBe(
      'sara@example.test',
    )
  })
})
