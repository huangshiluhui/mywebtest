import LoginIcon from '@/components/SvgIcon/LoginIcon.vue'

const svgRequired = require.context('./svg', false, /\.svg$/)
svgRequired.keys().forEach((item) => svgRequired(item))

export default (app) => {
    app.component('login-icon', LoginIcon)
}
