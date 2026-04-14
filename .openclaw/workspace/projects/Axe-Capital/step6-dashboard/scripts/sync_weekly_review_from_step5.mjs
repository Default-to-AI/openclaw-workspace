import fs from 'node:fs'
import path from 'node:path'

const dashboardPublic = path.resolve('public')
const src = path.resolve('..', 'step5-portfolio-tracking', 'reports', 'weekly-review-latest.json')
const dest = path.join(dashboardPublic, 'weekly-review-latest.json')

if (!fs.existsSync(src)) {
  console.error(`Missing source: ${src}`)
  process.exit(1)
}

fs.mkdirSync(dashboardPublic, { recursive: true })
fs.copyFileSync(src, dest)
console.log(`Copied weekly review -> ${dest}`)

