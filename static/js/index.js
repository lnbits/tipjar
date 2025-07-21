const mapTipJar = function (obj) {
  obj.date = Quasar.date.formatDate(
    new Date(obj.time * 1000),
    'YYYY-MM-DD HH:mm'
  )
  obj.fsat = new Intl.NumberFormat(LOCALE).format(obj.amount)
  obj.displayUrl = ['/tipjar/', obj.id].join('')
  return obj
}

window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.windowMixin],
  data() {
    return {
      tipjars: [],
      tips: [],
      walletLinks: [],
      hasSatsPay: true,
      tipjarsTable: {
        columns: [
          {
            name: 'id',
            align: 'left',
            label: 'ID',
            field: 'id'
          },
          {
            name: 'name',
            align: 'left',
            label: 'Donatee',
            field: 'name'
          },
          {
            name: 'wallet',
            align: 'left',
            label: 'Wallet',
            field: 'wallet'
          },
          {
            name: 'onchain address',
            align: 'left',
            label: 'Onchain Address',
            field: 'onchain'
          },
          {
            name: 'onchain limit',
            align: 'left',
            label: 'Limit (Dust)',
            field: 'onchain_limit'
          },
          {
            name: 'webhook',
            align: 'left',
            label: 'Webhook',
            field: 'webhook'
          }
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      tipsTable: {
        columns: [
          {
            name: 'tipjar',
            align: 'left',
            label: 'TipJar',
            field: 'tipjar'
          },
          {name: 'id', align: 'left', label: 'Charge ID', field: 'id'},
          {name: 'name', align: 'left', label: 'Donor', field: 'name'},
          {
            name: 'message',
            align: 'left',
            label: 'Message',
            field: 'message'
          },
          {name: 'sats', align: 'left', label: 'Sats', field: 'sats'}
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      tipjarDialog: {
        show: false,
        chain: false,
        data: {}
      }
    }
  },
  methods: {
    getWalletLinks() {
      LNbits.api
        .request(
          'GET',
          '/watchonly/api/v1/wallet',
          this.g.user.wallets[0].inkey
        )
        .then((response) => {
          for (i = 0; i < response.data.length; i++) {
            this.walletLinks.push(response.data[i].id)
          }
          return
        })
        .catch(LNbits.utils.notifyApiError)
    },
    getTips() {
      LNbits.api
        .request('GET', '/tipjar/api/v1/tips', this.g.user.wallets[0].adminkey)
        .then((response) => {
          this.tips = response.data.map((obj) => {
            return mapTipJar(obj)
          })
        })
    },
    deleteTip(tipId) {
      const tips = _.findWhere(this.tips, {id: tipId})

      LNbits.utils
        .confirmDialog('Are you sure you want to delete this tip?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              '/tipjar/api/v1/tips/' + tipId,
              _.findWhere(this.g.user.wallets, {id: tips.wallet}).adminkey
            )
            .then((response) => {
              this.tips = _.reject(this.tips, (obj) => {
                return obj.id == tipId
              })
            })
            .catch(LNbits.utils.notifyApiError)
        })
    },
    exporttipsCSV() {
      LNbits.utils.exportCSV(this.tipsTable.columns, this.tips)
    },

    getTipJars() {
      LNbits.api
        .request(
          'GET',
          '/tipjar/api/v1/tipjars',
          this.g.user.wallets[0].adminkey
        )
        .then((response) => {
          this.tipjars = response.data.map((obj) => {
            return mapTipJar(obj)
          })
        })
    },
    sendTipJarData() {
      const wallet = _.findWhere(this.g.user.wallets, {
        id: this.tipjarDialog.data.wallet
      })
      const data = this.tipjarDialog.data

      this.createTipJar(wallet, data)
    },

    createTipJar(wallet, data) {
      LNbits.api
        .request('POST', '/tipjar/api/v1/tipjars', wallet.adminkey, data)
        .then((response) => {
          this.tipjars.push(mapTipJar(response.data))
          this.tipjarDialog.show = false
          this.tipjarDialog.data = {}
        })
        .catch(LNbits.utils.notifyApiError)
    },
    updatetipjarDialog(tipjarId) {
      const link = _.findWhere(this.tipjars, {id: tipjarId})

      this.tipjarDialog.data.id = link.id
      this.tipjarDialog.data.wallet = link.wallet
      this.tipjarDialog.data.name = link.name
      this.tipjarDialog.data.webhook = link.webhook
      this.tipjarDialog.data.onchain_limit = link.onchain_limit
      this.tipjarDialog.chain = link.onchain != null
      this.tipjarDialog.show = true
    },
    deleteTipJar(tipjarsId) {
      const tipjars = _.findWhere(this.tipjars, {id: tipjarsId})

      LNbits.utils
        .confirmDialog('Are you sure you want to delete this tipjar link?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              '/tipjar/api/v1/tipjars/' + tipjarsId,
              _.findWhere(this.g.user.wallets, {id: tipjars.wallet}).adminkey
            )
            .then((response) => {
              this.tipjars = _.reject(this.tipjars, (obj) => {
                return obj.id == tipjarsId
              })
            })
            .catch(LNbits.utils.notifyApiError)
        })
    },
    exporttipjarsCSV() {
      LNbits.utils.exportCSV(this.tipjarsTable.columns, this.tipjars)
    },
    checkSatsPay() {
      if (!this.g.user.extensions.includes('satspay')) {
        this.hasSatsPay = false
        Quasar.Notify.create({
          type: 'negative',
          message: 'You need to install and enable the SatsPay extension to use TipJar.'
        })
      }
    }
  },

  created() {
    this.checkSatsPay()
    if (this.g.user.wallets.length && this.hasSatsPay) {
      this.getWalletLinks()
      this.getTipJars()
      this.getTips()
    }
  }
})
