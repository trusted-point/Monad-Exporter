from prometheus_client import Gauge, CollectorRegistry

registry = CollectorRegistry(auto_describe=True)

MON_PRICE_USD = Gauge(
    "monad_token_price_usd",
    "MON token price in USD",
    ["source"],
    registry=registry,
)

WALLET_BAL_WEI = Gauge(
    "monad_wallet_balance_wei",
    "Wallet balance in wei",
    ["address", "tag"],
    registry=registry,
)

STAKING_STAKE_WEI = Gauge(
    "monad_staking_stake_wei",
    "Delegator stake (wei) from staking contract",
    ["address", "tag", "validator_id"],
    registry=registry,
)

STAKING_TOTAL_REWARDS_WEI = Gauge(
    "monad_staking_rewards_wei",
    "Delegator rewards (wei) from staking contract",
    ["address", "tag", "validator_id"],
    registry=registry,
)