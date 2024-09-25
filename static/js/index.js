const mapTipJar = function (obj) {
  obj.date = Quasar.utils.date.formatDate(
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
    getWalletLinks: function () {
      var self = this

      LNbits.api
        .request(
          'GET',
          '/watchonly/api/v1/wallet',
          this.g.user.wallets[0].inkey
        )
        .then(function (response) {
          console.log(response.data)
          for (i = 0; i < response.data.length; i++) {
            self.walletLinks.push(response.data[i].id)
          }
          return
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    getTips: function () {
      var self = this

      LNbits.api
        .request('GET', '/tipjar/api/v1/tips', this.g.user.wallets[0].adminkey)
        .then(function (response) {
          self.tips = response.data.map(function (obj) {
            return mapTipJar(obj)
          })
        })
    },
    deleteTip: function (tipId) {
      var self = this
      var tips = _.findWhere(this.tips, {id: tipId})

      LNbits.utils
        .confirmDialog('Are you sure you want to delete this tip?')
        .onOk(function () {
          LNbits.api
            .request(
              'DELETE',
              '/tipjar/api/v1/tips/' + tipId,
              _.findWhere(self.g.user.wallets, {id: tips.wallet}).adminkey
            )
            .then(function (response) {
              self.tips = _.reject(self.tips, function (obj) {
                return obj.id == ticketId
              })
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error)
            })
        })
    },
    exporttipsCSV: function () {
      LNbits.utils.exportCSV(this.tipsTable.columns, this.tips)
    },

    getTipJars: function () {
      var self = this

      LNbits.api
        .request(
          'GET',
          '/tipjar/api/v1/tipjars',
          this.g.user.wallets[0].adminkey
        )
        .then(function (response) {
          self.tipjars = response.data.map(function (obj) {
            return mapTipJar(obj)
          })
        })
    },
    sendTipJarData: function () {
      var wallet = _.findWhere(this.g.user.wallets, {
        id: this.tipjarDialog.data.wallet
      })
      var data = this.tipjarDialog.data

      this.createTipJar(wallet, data)
    },

    createTipJar: function (wallet, data) {
      var self = this
      LNbits.api
        .request('POST', '/tipjar/api/v1/tipjars', wallet.adminkey, data)
        .then(function (response) {
          self.tipjars.push(mapTipJar(response.data))
          self.tipjarDialog.show = false
          self.tipjarDialog.data = {}
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    updatetipjarDialog: function (tipjarId) {
      var link = _.findWhere(this.tipjars, {id: tipjarId})

      this.tipjarDialog.data.id = link.id
      this.tipjarDialog.data.wallet = link.wallet
      this.tipjarDialog.data.name = link.name
      this.tipjarDialog.data.webhook = link.webhook
      this.tipjarDialog.data.onchain_limit = link.onchain_limit
      this.tipjarDialog.chain = link.onchain != null
      this.tipjarDialog.show = true
    },
    deleteTipJar: function (tipjarsId) {
      var self = this
      var tipjars = _.findWhere(this.tipjars, {id: tipjarsId})

      LNbits.utils
        .confirmDialog('Are you sure you want to delete this tipjar link?')
        .onOk(function () {
          LNbits.api
            .request(
              'DELETE',
              '/tipjar/api/v1/tipjars/' + tipjarsId,
              _.findWhere(self.g.user.wallets, {id: tipjars.wallet}).adminkey
            )
            .then(function (response) {
              self.tipjars = _.reject(self.tipjars, function (obj) {
                return obj.id == tipjarsId
              })
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error)
            })
        })
    },
    exporttipjarsCSV: function () {
      LNbits.utils.exportCSV(this.tipjarsTable.columns, this.tipjars)
    }
  },

  created: function () {
    if (this.g.user.wallets.length) {
      this.getWalletLinks()
      this.getTipJars()
      this.getTips()
      // this.getServices()
    }
  }
})
