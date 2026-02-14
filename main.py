from utils.args import args
from utils.logger import logger
from src.metrics import (
    registry,
    MON_PRICE_USD,
    WALLET_BAL_WEI,
    STAKING_STAKE_WEI,
    STAKING_TOTAL_REWARDS_WEI
)
from src.staking_getters import get_delegator

from dotenv import load_dotenv
import os, yaml, requests, time
from web3 import Web3
from prometheus_client import start_http_server, Gauge

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def update_mon_price(api_key: str) -> None:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": api_key}
    params = {"symbol": "MON", "convert": "USD"}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    MON_PRICE_USD.labels(source="cmc").set(float(data["data"]["MON"]["quote"]["USD"]["price"]))

def update_wallet_balances(w3: Web3, wallet: dict) -> None:
    addr = Web3.to_checksum_address(wallet["address"])
    tag = wallet.get("tag", "")
    bal = w3.eth.get_balance(addr)
    WALLET_BAL_WEI.labels(address=addr, tag=tag).set(bal)

def update_wallet_staking(w3, staking_contract: str, validator_id: int, wallet: dict) -> None:
    addr = Web3.to_checksum_address(wallet["address"])
    tag = wallet.get("tag", "")
    info = get_delegator(w3, staking_contract, validator_id, addr)
    stake_wei = int(info[0])
    total_rewards_wei = int(info[2])
    STAKING_STAKE_WEI.labels(address=addr, tag=tag, validator_id=str(validator_id)).set(stake_wei)
    STAKING_TOTAL_REWARDS_WEI.labels(address=addr, tag=tag, validator_id=str(validator_id)).set(total_rewards_wei)

def main():
    load_dotenv(override=True)

    api_key = os.getenv("CMC_API_KEY")
    if not api_key:
        raise RuntimeError("CMC_API_KEY missing in env")

    config = load_config(args.config_path)
    wallets = config.get("wallets", [])
    staking_contract = config["staking_contract"]
    validator_id = int(config["validator_id"])

    w3 = Web3(Web3.HTTPProvider(args.rpc_url))

    start_http_server(args.prometheus_port, addr=args.prometheus_host, registry=registry)
    logger.info(f"Metrics url: http://{args.prometheus_host}:{args.prometheus_port}/metrics")

    now = time.time()
    next_price   = now
    next_balance = now
    next_staking = now

    try:
        while True:
            now = time.time()

            if now >= next_price:
                try:
                    update_mon_price(api_key)
                    logger.info("Updated $MON price")
                except Exception:
                    logger.exception("Price update failed")
                next_price = now + args.token_price_update_interval

            if now >= next_balance:
                for wallet in wallets:
                    try:
                        update_wallet_balances(w3, wallet)
                        logger.info(f"Updated balance for {wallet.get('tag','')} {wallet.get('address','')}")
                    except Exception:
                        logger.exception(f"Balance update failed for {wallet.get('tag','')} {wallet.get('address','')}")
                next_balance = now + args.wallet_balance_update_interval

            if now >= next_staking:
                for wallet in wallets:
                    try:
                        update_wallet_staking(w3, staking_contract, validator_id, wallet)
                        logger.info(f"Updated staking for {wallet.get('tag','')} {wallet.get('address','')}")
                    except Exception:
                        logger.exception(f"Staking update failed for {wallet.get('tag','')} {wallet.get('address','')}")
                next_staking = now + args.staking_update_interval

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully.")
        return

if __name__ == "__main__":
    main()