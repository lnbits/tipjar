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
      coreOnchainWallets: [],
      loadingOnchainWallets: false,
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
            label: 'Onchain Wallet',
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
  computed: {
    editingTipjar() {
      return this.tipjars.find(jar => jar.id === this.tipjarDialog.data.id)
    },
    lightningWalletOptions() {
      const walletIds = this.g.user.wallets
        .filter(wallet => wallet.canReceivePayments)
        .map(wallet => wallet.id)
      return this.g.user.walletOptions.filter(wallet =>
        walletIds.includes(wallet.value)
      )
    },
    onchainWalletOptions() {
      const core = this.coreOnchainWallets.map(wallet => ({
        label: `LNbits: ${wallet.name}${wallet.status === 'ready' ? '' : ' (Not ready)'}`,
        value: `core:${wallet.id}`
      }))
      const watchonly = this.walletLinks.map(wallet => ({
        label: `Watchonly: ${wallet.title || wallet.id}`,
        value: wallet.id
      }))
      return [...core, ...watchonly]
    },
    selectedCoreWallet() {
      const reference = this.tipjarDialog.data.onchain
      if (!reference?.startsWith('core:')) return null
      return (
        this.coreOnchainWallets.find(w => w.id === reference.slice(5)) || null
      )
    },
    hasCoreOnchainWallet() {
      return this.g.user.wallets.some(wallet => wallet.walletType === 'onchain')
    },
    onchainSelectionInvalid() {
      if (!this.tipjarDialog.chain) return false
      const reference = this.tipjarDialog.data.onchain
      if (reference && reference === this.editingTipjar?.onchain) return false
      return (
        !this.onchainWalletOptions.some(option => option.value === reference) ||
        (reference?.startsWith('core:') &&
          this.selectedCoreWallet?.status !== 'ready')
      )
    }
  },
  methods: {
    async getWalletLinks() {
      if (this.loadingOnchainWallets) return
      this.loadingOnchainWallets = true
      this.walletLinks = []
      this.coreOnchainWallets = []
      const inkey = this.g.user.wallets[0].inkey
      try {
        const {
          data: {network}
        } = await LNbits.api.request('GET', '/satspay/api/v1/settings/public')
        const core = LNbits.api
          .request('GET', '/satspay/api/v1/onchain-wallets', inkey)
          .then(({data}) => {
            this.coreOnchainWallets = data.filter(
              wallet => wallet.network === network
            )
          })
          .catch(LNbits.utils.notifyApiError)
        if (this.g.user.extensions.includes('watchonly')) {
          await Promise.all([core, this.getWatchonlyWallets(network, inkey)])
        } else {
          await core
        }
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      } finally {
        this.loadingOnchainWallets = false
      }
    },
    async getWatchonlyWallets(network, inkey) {
      try {
        const {data: config} = await LNbits.api.request(
          'GET',
          '/watchonly/api/v1/config',
          inkey
        )
        if (config.network !== network) {
          this.$q.notify({
            type: 'warning',
            message: `Watchonly must use the SatsPay network (${network}).`
          })
          return
        }
        const {data} = await LNbits.api.request(
          'GET',
          `/watchonly/api/v1/wallet?network=${encodeURIComponent(network)}`,
          inkey
        )
        this.walletLinks = data
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },
    createOnchainWallet() {
      this.g.newWalletType = 'onchain'
    },
    openOnchainWallet(walletId) {
      this.$router.push({path: '/wallet', query: {wal: walletId}})
    },
    openTipjarDialog() {
      this.tipjarDialog.data = {}
      this.tipjarDialog.chain = false
      this.tipjarDialog.show = true
    },
    getTips() {
      LNbits.api
        .request('GET', '/tipjar/api/v1/tips', this.g.user.wallets[0].adminkey)
        .then(response => {
          this.tips = response.data.map(obj => {
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
            .then(response => {
              this.tips = _.reject(this.tips, obj => {
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
        .then(response => {
          this.tipjars = response.data.map(obj => {
            return mapTipJar(obj)
          })
        })
    },
    sendTipJarData() {
      if (this.onchainSelectionInvalid) return
      const wallet = _.findWhere(this.g.user.wallets, {
        id: this.editingTipjar?.wallet || this.tipjarDialog.data.wallet
      })
      const data = {
        ...this.tipjarDialog.data,
        onchain: this.tipjarDialog.chain ? this.tipjarDialog.data.onchain : null
      }
      return LNbits.api
        .request(
          data.id ? 'PUT' : 'POST',
          '/tipjar/api/v1/tipjars' + (data.id ? `/${data.id}` : ''),
          wallet.adminkey,
          data
        )
        .then(response => {
          const tipjar = mapTipJar(response.data)
          if (data.id) {
            this.tipjars = this.tipjars.map(jar =>
              jar.id === data.id ? tipjar : jar
            )
          } else {
            this.tipjars.push(tipjar)
          }
          this.tipjarDialog.show = false
          this.tipjarDialog.data = {}
        })
        .catch(LNbits.utils.notifyApiError)
    },
    updatetipjarDialog(tipjarId) {
      const link = _.findWhere(this.tipjars, {id: tipjarId})

      this.tipjarDialog.data = {...link}
      this.tipjarDialog.chain = Boolean(link.onchain)
      this.tipjarDialog.show = true
      if (this.tipjarDialog.chain) this.getWalletLinks()
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
            .then(response => {
              this.tipjars = _.reject(this.tipjars, obj => {
                return obj.id == tipjarsId
              })
              this.getTips()
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
          message:
            'You need to install and enable the SatsPay extension to use TipJar.'
        })
      }
    }
  },

  created() {
    this.checkSatsPay()
    if (this.g.user.wallets.length && this.hasSatsPay) {
      this.getTipJars()
      this.getTips()
    }
  }
})
