window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.windowMixin],
  data() {
    return {
      paymentReq: null,
      redirectUrl: null,
      tipjarId: tipjarId,
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
            tipjar: this.tipjarId,
            message: this.tipDialog.data.message
          }
        )
        this.redirectUrl = data.redirect_url
        window.location.href = this.redirectUrl
      } catch (error) {
        let detail = error?.response?.data?.detail
        if (detail) {
          if (typeof detail === 'object') {
            detail = JSON.stringify(detail)
          }
          this.$q.notify({
            type: 'negative',
            message: "Something went wrong! Contact the TipJar owner.",
            caption: detail
          })
        } else {
          LNbits.utils.notifyApiError(error)
        }
      }
    }
  }
})
