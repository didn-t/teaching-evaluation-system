import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

process.env.UNI_PLATFORM = process.env.UNI_PLATFORM || 'mp-weixin'
process.env.UNI_INPUT_DIR = process.env.UNI_INPUT_DIR || 'src'

export default defineConfig({
  plugins: [uni.default()],
})
