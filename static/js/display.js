window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.windowMixin],
  data() {
    return {
      paymentReq: null,
      redirectUrl: null,
      tipDialog: {
        show: false,
        data: {
          name: '',
          sats: '',
          message: ''
        }
      }
    }
  },
  methods: {
    async invoice() {
      try {
        const {data} = await LNbits.api.request(
          'POST',
          '/tipjar/api/v1/tips',
          null,
          {
            name: this.tipDialog.data.name,
            sats: this.tipDialog.data.sats,
            tipjar: '{{ tipjar_id }}',
            message: this.tipDialog.data.message
          }
        )
        this.redirectUrl = data.redirect_url
        window.location.href = this.redirectUrl
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    }
  }
})
