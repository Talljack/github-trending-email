import createEslintConfig from 'talljack-eslint-config'

export default createEslintConfig({
  typescript: true,
  formatters: true,
  jsdoc: false,
  rules: {
    '@typescript-eslint/ban-ts-comment': 'off',
    'no-console': 'off',
  },
})
