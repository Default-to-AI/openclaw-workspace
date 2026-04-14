import fs from 'node:fs'
import path from 'node:path'

const root = path.resolve(process.cwd(), 'public')
const portfolioPath = path.join(root, 'portfolio.json')
const targetsPath = path.join(root, 'targets.json')

if (!fs.existsSync(portfolioPath)) {
  console.error(`Missing ${portfolioPath}`)
  process.exit(1)
}

const portfolio = JSON.parse(fs.readFileSync(portfolioPath, 'utf8'))
const symbols = (portfolio.positions ?? []).map((p) => p.symbol).filter(Boolean)

let targets = {
  version: 1,
  as_of: portfolio.review_date ?? null,
  notes: 'Per-position targets/stops. Edit manually. id must be unique and stable.',
  positions: []
}

if (fs.existsSync(targetsPath)) {
  try {
    targets = JSON.parse(fs.readFileSync(targetsPath, 'utf8'))
  } catch {
    // keep default scaffold
  }
}

const existing = new Map()
for (const p of targets.positions ?? []) {
  const key = p.id ?? p.symbol
  if (key) existing.set(key, p)
}

const next = symbols.map((sym) => {
  const prev = existing.get(sym)
  if (prev) return { id: sym, symbol: sym, ...prev, id: sym, symbol: sym }
  return {
    id: sym,
    symbol: sym,
    profit_target_price: null,
    profit_target_pct: null,
    stop_price: null,
    stop_pct: null,
    comment: ''
  }
})

targets.positions = next

fs.writeFileSync(targetsPath, JSON.stringify(targets, null, 2) + '\n')
console.log(`Synced ${next.length} positions -> ${path.relative(process.cwd(), targetsPath)}`)

