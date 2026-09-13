import { shallowRef } from 'vue'
import type { ReadingResponse } from '@/features/readings/types'

const currentResult = shallowRef<ReadingResponse>()

export function useReadingResultState() {
  function setResult(result: ReadingResponse): void {
    currentResult.value = result
  }

  function clearResult(): void {
    currentResult.value = undefined
  }

  return { currentResult, setResult, clearResult }
}
