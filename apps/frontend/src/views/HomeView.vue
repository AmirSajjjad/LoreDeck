<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'

const readingSteps = [
  {
    number: '۱',
    title: 'پرسش را در ذهن نگه دارید',
    description: 'لحظه‌ای مکث کنید و پرسشی روشن یا موضوعی که برایتان اهمیت دارد در نظر بگیرید.',
  },
  {
    number: '۲',
    title: 'دسته و چیدمان را انتخاب کنید',
    description: 'دستهٔ کارت و چیدمان یک‌کارتی یا سه‌کارتی متناسب با پرسش خود را برگزینید.',
  },
  {
    number: '۳',
    title: 'کارت‌ها را دریافت کنید',
    description: 'کارت‌های خوانش و تفسیر آن‌ها را با آرامش مرور کنید.',
  },
] as const
</script>

<template>
  <div class="grid w-full gap-section overflow-hidden">
    <section
      class="relative isolate grid items-center gap-10 py-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(18rem,0.85fr)] lg:py-12"
      aria-labelledby="home-heading"
    >
      <div
        class="pointer-events-none absolute -start-24 top-0 -z-10 size-72 rounded-full border border-accent/15"
        aria-hidden="true"
      />
      <div class="max-w-3xl">
        <p class="text-sm font-semibold tracking-wide text-accent">روایت در میان کارت‌ها</p>
        <h1 id="home-heading" class="mt-3 text-4xl font-bold sm:text-5xl lg:text-6xl">لور دک</h1>
        <p class="mt-6 max-w-2xl text-lg leading-9 text-muted sm:text-xl">
          فضایی آرام برای خوانش تاروت؛ پرسش خود را در ذهن نگه دارید، چیدمان را انتخاب کنید و معنای
          کارت‌ها را در کنار روایت شخصی خود ببینید.
        </p>
        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <RouterLink
            class="inline-flex min-h-11 items-center justify-center rounded-control border border-accent bg-accent px-6 py-2.5 font-semibold text-accent-contrast transition-colors hover:bg-accent/90"
            :to="{ name: 'reading-create' }"
          >
            شروع یک خوانش
          </RouterLink>
        </div>
        <p class="mt-4 text-sm text-muted">برای شروع خوانش نیازی به ورود به حساب نیست.</p>
      </div>

      <div class="relative mx-auto grid w-full max-w-sm place-items-center py-8" aria-hidden="true">
        <div class="absolute size-64 rounded-full border border-line/60 sm:size-72" />
        <div
          class="absolute size-48 rotate-12 rounded-card border border-line bg-surface shadow-elevated"
        />
        <div
          class="relative grid aspect-[3/4] w-40 -rotate-6 place-items-center rounded-card border border-accent/60 bg-elevated shadow-elevated sm:w-44"
        >
          <span
            class="grid size-20 place-items-center rounded-full border border-accent/50 text-4xl text-accent"
            >✦</span
          >
        </div>
      </div>
    </section>

    <section aria-labelledby="reading-flow-heading">
      <div class="max-w-2xl">
        <p class="text-sm font-semibold text-accent">مسیر خوانش</p>
        <h2 id="reading-flow-heading" class="mt-2 text-3xl font-bold">سه قدم ساده</h2>
        <p class="mt-3 text-muted">خوانش را بدون شتاب آغاز کنید و هر مرحله را آگاهانه پیش ببرید.</p>
      </div>
      <ol class="mt-8 grid gap-4 md:grid-cols-3">
        <li v-for="step in readingSteps" :key="step.number">
          <BaseCard class="h-full">
            <span
              class="grid size-10 place-items-center rounded-full border border-accent/60 font-bold text-accent"
              aria-hidden="true"
              >{{ step.number }}</span
            >
            <h3 class="mt-5 text-xl font-bold">{{ step.title }}</h3>
            <p class="mt-3 text-sm leading-7 text-muted">{{ step.description }}</p>
          </BaseCard>
        </li>
      </ol>
    </section>

    <section aria-labelledby="spread-heading">
      <BaseCard elevated>
        <div class="grid gap-8 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)] lg:items-start">
          <div>
            <p class="text-sm font-semibold text-accent">چیدمان‌ها</p>
            <h2 id="spread-heading" class="mt-2 text-3xl font-bold">به اندازهٔ پرسش شما</h2>
            <p class="mt-3 text-muted">
              برای تأملی کوتاه یا نگاهی چندوجهی، یکی از دو چیدمان MVP را انتخاب کنید.
            </p>
          </div>
          <div class="grid gap-4 sm:grid-cols-2">
            <article class="rounded-card border border-line bg-surface-secondary p-5">
              <p class="text-sm text-accent">یک کارت</p>
              <h3 class="mt-2 text-xl font-bold">خوانش یک‌کارتی</h3>
              <p class="mt-3 text-sm leading-7 text-muted">
                یک کارت برای تمرکز بر لحظهٔ اکنون و نگاه مختصر به پرسش.
              </p>
            </article>
            <article class="rounded-card border border-line bg-surface-secondary p-5">
              <p class="text-sm text-accent">سه کارت</p>
              <h3 class="mt-2 text-xl font-bold">خوانش سه‌کارتی</h3>
              <p class="mt-3 text-sm leading-7 text-muted">
                سه کارت در جایگاه‌های گذشته، اکنون و آینده برای دیدن مسیر پرسش.
              </p>
            </article>
          </div>
        </div>
      </BaseCard>
    </section>

    <section class="pb-4 text-center" aria-labelledby="closing-heading">
      <h2 id="closing-heading" class="text-2xl font-bold">پرسش شما آماده است؟</h2>
      <p class="mx-auto mt-3 max-w-xl text-muted">لحظه‌ای مکث کنید و خوانش خود را آغاز کنید.</p>
      <RouterLink
        class="mt-6 inline-flex min-h-11 items-center justify-center rounded-control border border-accent bg-accent px-6 py-2.5 font-semibold text-accent-contrast transition-colors hover:bg-accent/90"
        :to="{ name: 'reading-create' }"
        >رفتن به خوانش تازه</RouterLink
      >
    </section>
  </div>
</template>
