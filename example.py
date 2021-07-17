import os
import asyncio
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException
from datetime import datetime, timedelta

# Note: for information on how to use this example code please read https://metaapi.cloud/docs/client/usingCodeExamples

token = os.getenv('TOKEN') or 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJhZmE2YWUyMWUzZGY2ZDc3NzVmNGJjMDFiNDlmM2QwNSIsInBlcm1pc3Npb25zIjpbXSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaWF0IjoxNjI2NTUxNjY4LCJyZWFsVXNlcklkIjoiYWZhNmFlMjFlM2RmNmQ3Nzc1ZjRiYzAxYjQ5ZjNkMDUifQ.B3szVkT3HnTBiiGDknaOaYgicdIiBtJ4UbqUH46ZHZK1GUBBuexYXyiYEE7QQtsaTzXD5LhLTtox-jwo2ZHB2Ym-HV7zh1SaRhCb0BNgVwMYsjhdOVYdxsD0eb1ZPRY5BWXAQYZphpuWl4YrBl10S7jATLXUss5_Ann95zcmOaTnJ2gV-HLnrUWVhzCbs758HD8p5cgSr2nBNCbUcDM72YjA891-Jrg7VWFYk-P4vjUnq32e-PGwhgdQB3zXAIcQUaWNSjFCeRkmUV1CeLWUVk9eA9H3N73-Mafy21WaZ_XuQadrPuY583jVLluXMKQFAj0l_3C7M4WJpqq5NqyXHAn1-C_n4_fcWurwLYWk6IRkUt4nSzl1ATAwQdM7cGofHnt6oSGCHjOe38ZU1CIxKlWfqHuMRvRltYmr0zm4qSlqe0FwHqetICFMpGuTYJDvOBW1XSadRq7MlDUCvKp_01-zmZd-GHb66rYqppN3j9SJCtXKqUXikE25Sr0Cwaef1fF0uhV3QtX8VkDBg4fYKDmRUzQ_L52Aj-ADGXDqaLagi8bgFHP-I_SyA_6OGpOyUpoftr30CZ39QfVpZGHdb3YLkd7UG8S36S84AsivSobotwpcH0Un-qPoFa3xrS5ALO8BbacVNHz15U13inF-ArXF7eRg9ZfWCy_2N56kack'
accountId = os.getenv('ACCOUNT_ID') or 'f920eee0-258f-4336-972a-8c73ff0ca226'


async def test_meta_api_synchronization():
    api = MetaApi(token)
    try:
        account = await api.metatrader_account_api.get_account(accountId)
        initial_state = account.state
        deployed_states = ['DEPLOYING', 'DEPLOYED']

        if initial_state not in deployed_states:
            #  wait until account is deployed and connected to broker
            print('Deploying account')
            await account.deploy()

        print('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        # connect to MetaApi API
        connection = await account.connect()

        # wait until terminal state synchronized to the local state
        print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
        await connection.wait_synchronized()

        # invoke RPC API (replace ticket numbers with actual ticket numbers which exist in your MT account)
        print('Testing MetaAPI RPC API')
        print('account information:', await connection.get_account_information())
        print('positions:', await connection.get_positions())
        # print(await connection.get_position('1234567'))
        print('open orders:', await connection.get_orders())
        # print(await connection.get_order('1234567'))
        print('history orders by ticket:', await connection.get_history_orders_by_ticket('1234567'))
        print('history orders by position:', await connection.get_history_orders_by_position('1234567'))
        print('history orders (~last 3 months):',
              await connection.get_history_orders_by_time_range(datetime.utcnow() - timedelta(days=90),
                                                                datetime.utcnow()))
        print('history deals by ticket:', await connection.get_deals_by_ticket('1234567'))
        print('history deals by position:', await connection.get_deals_by_position('1234567'))
        print('history deals (~last 3 months):',
              await connection.get_deals_by_time_range(datetime.utcnow() - timedelta(days=90), datetime.utcnow()))

        # trade
        print('Submitting pending order')
        try:
            result = await connection.create_limit_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0,
                                                             {'comment': 'comm', 'clientId': 'TE_GBPUSD_7hyINWqAlE'})
            print('Trade successful, result code is ' + result['stringCode'])
        except Exception as err:
            print('Trade failed with error:')
            print(api.format_error(err))
        if initial_state not in deployed_states:
            # undeploy account if it was undeployed
            print('Undeploying account')
            await account.undeploy()

    except Exception as err:
        print(api.format_error(err))

asyncio.run(test_meta_api_synchronization())
