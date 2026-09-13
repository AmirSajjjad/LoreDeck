import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ReadingResultCard from '@/features/readings/components/ReadingResultCard.vue'
import ReadingResultView from '@/features/readings/views/ReadingResultView.vue'
import { useReadingResultState } from '@/features/readings/readingResultState'
import type { ReadingResponse } from '@/features/readings/types'
import { renderWithApp } from './helpers/render'

const oneCard: ReadingResponse = {
  cards: [
    {
      position: 'present',
      orientation: 'upright',
      card: {
        title: 'خورشید <script>alert(1)</script>',
        description: null,
        number: null,
        image_path: null,
      },
      story: 'روایت روشن',
    },
  ],
  summary: 'جمع‌بندی',
}
const firstCard = oneCard.cards[0]

describe('reading result components', () => {
  it('renders nullable card fields and untrusted text as plain text', async () => {
    const item = {
      ...firstCard,
      card: { ...firstCard.card, image_path: null },
    }
    const wrapper = mount(ReadingResultCard, { props: { item } })
    expect(wrapper.text()).toContain('خورشید <script>alert(1)</script>')
    expect(wrapper.find('script').exists()).toBe(false)
    expect(wrapper.text()).toContain('جایگاه: اکنون')
    expect(wrapper.text()).toContain('جهت: مستقیم')
    expect(wrapper.text()).toContain('تصویر کارت در دسترس نیست')
  })

  it('preserves three-card response ordering and optional summary', async () => {
    const state = useReadingResultState()
    state.setResult({
      cards: ['گذشته', 'اکنون', 'آینده'].map((title, index) => ({
        position: ['past', 'present', 'future'][index] as 'past' | 'present' | 'future',
        orientation: 'upright' as const,
        card: { title, description: null, number: index + 1, image_path: null },
        story: `روایت ${title}`,
      })),
      summary: 'نتیجهٔ کلی',
    })
    const { wrapper } = await renderWithApp(ReadingResultView)
    await flushPromises()
    const titles = wrapper.findAll('.reading-card h2').map((node) => node.text())
    expect(titles).toEqual(['گذشته', 'اکنون', 'آینده'])
    expect(wrapper.text()).toContain('نتیجهٔ کلی')
  })

  it('offers a new reading when in-memory state is missing or malformed', async () => {
    const missing = await renderWithApp(ReadingResultView)
    expect(missing.wrapper.text()).toContain('نتیجه‌ای برای نمایش وجود ندارد')
    expect(missing.wrapper.get('a').attributes('href')).toBe('/readings/new')
    missing.wrapper.unmount()

    useReadingResultState().setResult({ cards: [], summary: 12 } as never)
    const malformed = await renderWithApp(ReadingResultView)
    expect(malformed.wrapper.text()).toContain('نتیجهٔ خوانش قابل نمایش نیست')
  })
})
