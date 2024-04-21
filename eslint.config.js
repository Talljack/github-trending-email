import createEslintConfig from 'talljack-eslint-config'

export default createEslintConfig({
  typescript: true,
  formatters: true,
  rules: {
    '@typescript-eslint/ban-ts-comment': 'off',
    'no-console': 'off',
  },
}, {
  ignores: [
    '**/lib',
  ],
})
