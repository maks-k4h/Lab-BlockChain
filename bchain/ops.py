from pathlib import Path
from . import wallet, chain, transaction


################################################################################
#  Wallet Operations
################################################################################

def wallet_create(
        path: Path
) -> None:
    print('Creating wallet...')
    w = wallet.Wallet.generate()
    print('Wallet created. Address:')
    print(w.b64_address)
    print('Saving...')
    w.to_file(path)


def wallet_info(
        p_wallet: Path,
) -> None:
    w = wallet.Wallet.from_file(p_wallet)
    print('Wallet address:', w.b64_address)


################################################################################
#  BlockChain Operations
################################################################################

def chain_create(
        dest: Path,
        p_wallet: Path,
) -> None:
    print('Loading wallet...')
    w = wallet.Wallet.from_file(p_wallet)
    print('Creating chain...')
    c = chain.Chain.new_chain(w.b64_address)
    c.to_file(dest)
    print('Done!')


def chain_info(
        p_chain: Path,
        block_limit: int = -1,
) -> None:
    c = chain.Chain.from_file(p_chain)
    c_verified = c.verify()
    print('Chain length:', c.length)
    print('First block:', c.blocks[0].b64_hash)
    print('Last block mined:', c.last_block.is_mined)
    print('Chain valid:', c_verified)
    if not c_verified:
        print('Abort. Not valid')
        return

    # calculate stats over balances
    if block_limit > 0:
        c_limited = c.get_subchain(block_limit)
    else:
        c_limited = c
    addresses = c_limited.addresses
    print('\nStatistics over addresses. Length of subchain:', c_limited.length)
    for address in addresses:
        b, b_min, b_max = c_limited.calculate_balance(address)
        if b == 0:
            continue
        print('\tBalance:', address)
        print('\t\tCurrent:', b)
        print('\t\tMin:', b_min)
        print('\t\tMax:', b_max)


def chain_mine(
        p_chain: Path,
        p_wallet: Path,
) -> None:
    c = chain.Chain.from_file(p_chain)
    if not c.verify():
        print('Chain invalid!')
        return
    if c.last_block.is_mined:
        print('Last block already mined!')
        return
    print('Loading wallet...')
    w = wallet.Wallet.from_file(p_wallet)
    print('Mining...')
    c.last_block.mine(w.b64_address)
    print('Mining succeeded! Saving the chain...')
    c.to_file(p_chain)
    print('Done!')


################################################################################
#  Transaction Operations
################################################################################

def transaction_create(
        p_wallet: Path,
        p_chain: Path,
        receiver: str,
        amount: int,
) -> None:
    print('Loading wallet...')
    w = wallet.Wallet.from_file(p_wallet)
    print('Loading and verifying chain...')
    c = chain.Chain.from_file(p_chain)
    if not c.verify():
        print('Invalid chain! Abort')
        return

    print('Creating new transaction...')
    t = transaction.Transaction(
        b64_sender=w.b64_address,
        b64_receiver=receiver,
        amount=amount,
    )
    print('Signing transaction...')
    t.sign(w)
    print('Adding transaction to the chain...')
    if not c.add_transaction(t):
        print('Abort')
        return
    c.to_file(p_chain)
    print('Done!')
