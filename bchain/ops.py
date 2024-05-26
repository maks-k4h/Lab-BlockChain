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
    print('Chain length:', len(c.blocks))
    print('First block:', c.blocks[0].b64_hash)
    print('Last block mined:', c.last_block.verify())
    print('Chain valid:', c.verify())


def chain_mine(
        p_chain: Path,
        p_wallet: Path,
) -> None:
    c = chain.Chain.from_file(p_chain)
    if not c.verify():
        print('Chain invalid!')
        return
    if c.last_block.verify(check_pow=True):
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
    c.add_transaction(t)
    c.to_file(p_chain)
    print('Done!')
