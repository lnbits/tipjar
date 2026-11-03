const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const test = require('node:test')
const vm = require('node:vm')

function page(request, extensions = ['watchonly']) {
  const context = {
    window: {},
    Vue: {createApp: component => component},
    Quasar: {date: {formatDate: () => ''}},
    LOCALE: 'en',
    _: {findWhere: (items, {id}) => items.find(item => item.id === id)},
    LNbits: {api: {request}, utils: {notifyApiError: () => {}}}
  }
  vm.runInNewContext(
    fs.readFileSync(path.join(__dirname, '../static/js/index.js'), 'utf8'),
    context
  )
  const component = context.window.app
  const state = {
    ...component.data(),
    ...component.methods,
    g: {
      user: {
        extensions,
        wallets: [{id: 'merchant', adminkey: 'admin', inkey: 'invoice'}]
      }
    }
  }
  for (const [name, get] of Object.entries(component.computed)) {
    Object.defineProperty(state, name, {get: () => get.call(state)})
  }
  return state
}

test('discovery filters by SatsPay network and tolerates Watchonly failure', async () => {
  const calls = []
  const state = page(async (method, url, key) => {
    calls.push([url, key])
    if (url.endsWith('/settings/public')) return {data: {network: 'Mainnet'}}
    if (url.endsWith('/onchain-wallets'))
      return {
        data: [
          {id: 'main', name: 'Main', status: 'ready', network: 'Mainnet'},
          {id: 'test', name: 'Test', status: 'ready', network: 'Testnet4'}
        ]
      }
    throw new Error('Watchonly unavailable')
  })

  await state.getWalletLinks()
  assert.deepEqual(
    Array.from(state.onchainWalletOptions, option => option.value),
    ['core:main']
  )
  assert.deepEqual(calls.slice(1), [
    ['/satspay/api/v1/onchain-wallets', 'invoice'],
    ['/watchonly/api/v1/config', 'invoice']
  ])
})

test('an existing jar can be edited without discovery and keeps its payment destination', async () => {
  const calls = []
  const state = page(async (method, url, key, data) => {
    if (method === 'GET') throw new Error('Discovery unavailable')
    calls.push({method, url, key})
    return {data}
  }, [])
  const jar = {
    id: 'jar',
    wallet: 'merchant',
    name: 'Before',
    onchain: 'core:chain'
  }
  state.tipjars = [jar]
  state.updatetipjarDialog(jar.id)
  state.tipjarDialog.data.name = 'After'
  await state.sendTipJarData()
  assert.deepEqual(calls, [
    {method: 'PUT', url: '/tipjar/api/v1/tipjars/jar', key: 'admin'}
  ])
  assert.equal(state.tipjars[0].onchain, 'core:chain')
  assert.equal(state.tipjars[0].name, 'After')
  assert.equal(jar.name, 'Before')
})
