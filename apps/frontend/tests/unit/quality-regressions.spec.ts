import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ErrorState from '@/components/common/ErrorState.vue'
import ReadingResultCard from '@/features/readings/components/ReadingResultCard.vue'
import { resolveProfileImageUrl } from '@/features/profile/utils/profileImage'

describe('quality regressions', () => {
  it('renders an actionable error state with a working retry control', async () => {
    const wrapper = mount(ErrorState, {
      props: { message: 'ارتباط برقرار نشد.', retryable: true },
    })
    expect(wrapper.get('[role="alert"]').text()).toContain('ارتباط برقرار نشد.')
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('retry')).toHaveLength(1)
  })

  it('lazy-loads card images and falls back after an image failure', async () => {
    const wrapper = mount(ReadingResultCard, {
      props: {
        item: {
          position: 'present',
          orientation: 'upright',
          card: {
            title: 'خورشید',
            description: null,
            number: 19,
            image_path: 'cards/sun.webp',
          },
          story: 'روایت',
        },
      },
    })
    const image = wrapper.get('img')
    expect(image.attributes('loading')).toBe('lazy')
    expect(image.attributes('decoding')).toBe('async')
    await image.trigger('error')
    expect(wrapper.find('img').exists()).toBe(false)
    expect(wrapper.get('[role="img"]').text()).toContain('تصویر کارت در دسترس نیست')
  })

  it('rejects executable profile-image schemes', () => {
    expect(resolveProfileImageUrl('javascript:alert(1)')).toBeUndefined()
    expect(resolveProfileImageUrl('data:text/html,unsafe')).toBeUndefined()
  })
})
