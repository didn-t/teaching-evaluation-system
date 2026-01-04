import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import fs from 'node:fs'
import path from 'node:path'

process.env.UNI_PLATFORM = process.env.UNI_PLATFORM || 'mp-weixin'
process.env.UNI_INPUT_DIR = process.env.UNI_INPUT_DIR || '.'

let resolvedOutDir = null

function syncStaticAssets(outDir) {
  const inputDir = process.env.UNI_INPUT_DIR || '.'
  const srcDir = path.resolve(process.cwd(), inputDir, 'static')
  const absOutDir = outDir ? path.resolve(process.cwd(), outDir) : null
  if (!absOutDir || !fs.existsSync(srcDir)) {
    return
  }
  const destDir = path.join(absOutDir, 'static')
  fs.mkdirSync(destDir, { recursive: true })
  fs.cpSync(srcDir, destDir, { recursive: true })

  const assetsMapFile = path.join(absOutDir, 'common', 'assets.js')
  const logoFile = path.join(srcDir, 'logo.png')
  if (!fs.existsSync(assetsMapFile) || !fs.existsSync(logoFile)) {
    return
  }
  const assetsMapContent = fs.readFileSync(assetsMapFile, 'utf8')
  const matches = [...assetsMapContent.matchAll(/"(\/assets\/[^"\\]+)"/g)]
  for (const m of matches) {
    const assetPath = m && m[1] ? String(m[1]) : ''
    if (!assetPath || !assetPath.includes('logo.') || !assetPath.endsWith('.png')) {
      continue
    }
    const assetRel = assetPath.replace(/^\//, '')
    const destAssetFile = path.join(absOutDir, assetRel)
    if (fs.existsSync(destAssetFile)) {
      continue
    }
    fs.mkdirSync(path.dirname(destAssetFile), { recursive: true })
    fs.copyFileSync(logoFile, destAssetFile)
  }
}

export default defineConfig({
  plugins: [uni.default(), {
    name: 'copy-uniapp-static',
    configResolved(config) {
      resolvedOutDir = config.build.outDir
    },
    // 22300417陈俫坤开发：开发和构建模式都复制静态文件
    buildStart() {
      // 开发模式下复制到 dist/dev/mp-weixin/static
      const devOutDir = path.resolve(process.cwd(), 'dist/dev/mp-weixin')
      if (fs.existsSync(devOutDir)) {
        syncStaticAssets(devOutDir)
      }
    },
    writeBundle() {
      syncStaticAssets(resolvedOutDir)
    }
  }],
})
