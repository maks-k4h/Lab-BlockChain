import argparse
from pathlib import Path

from . import ops


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='command', dest='command')

    wallet_parser = subparsers.add_parser(name='wallet')
    wallet_subparsers = wallet_parser.add_subparsers(title='wallet command', dest='wallet_command')
    wallet_create_parser = wallet_subparsers.add_parser(name='create', help='Create new wallet')
    wallet_create_parser.add_argument('--path', help='Where to save wallet information',
                                      default='wallet.wal', required=False)
    wallet_info_parser = wallet_subparsers.add_parser(name='info', help='Get wallet info')
    wallet_info_parser.add_argument('--wallet', help='Path to wallet file',)

    chain_parser = subparsers.add_parser(name='chain')
    chain_subparsers = chain_parser.add_subparsers(title='chain command', dest='chain_command')
    chain_create_parser = chain_subparsers.add_parser(name='create', help='Create new blockchain')
    chain_create_parser.add_argument('--path', help='Where to save blockchain information',
                                     default='chain.json', required=False)
    chain_create_parser.add_argument('--wallet', help='Wallet to use',
                                     default='wallet.wal', required=False)
    chain_info_parser = chain_subparsers.add_parser(name='info', help='Get blockchain info')
    chain_info_parser.add_argument('--chain', help='Path to chain file',
                                   default='chain.json', required=False)
    chain_parser.add_argument('--block-limit', type=int, default=-1, required=False,
                              help='Number of first blocks to check (-1 to check all)')
    chain_mine_parser = chain_subparsers.add_parser(name='mine', help='Mine new block')
    chain_mine_parser.add_argument('--chain', help='Path to chain file',
                                   default='chain.json', required=False)
    chain_mine_parser.add_argument('--wallet', help='Wallet to use',
                                   default='wallet.wal', required=False)

    transaction_parser = subparsers.add_parser(name='transaction')
    transaction_subparsers = transaction_parser.add_subparsers(title='transaction command', dest='transaction_command')
    transaction_create_parser = transaction_subparsers.add_parser(name='create', help='Create new transaction')
    transaction_create_parser.add_argument('--wallet', help='Path to wallet',
                                           default='wallet.wal', required=False)
    transaction_create_parser.add_argument('--chain', help='Path to chain file',
                                           default='chain.json', required=False)
    transaction_create_parser.add_argument('--receiver', help='Public address of receiver',)
    transaction_create_parser.add_argument('--amount', type=int, help='Amount to send',)


    args = parser.parse_args()

    if args.command == 'wallet':
        if args.wallet_command == 'create':
            ops.wallet_create(
                path=Path(args.path),
            )
        elif args.wallet_command == 'info':
            ops.wallet_info(
                p_wallet=Path(args.wallet),
            )
        else:
            wallet_parser.print_help()
    elif args.command == 'chain':
        if args.chain_command == 'create':
            ops.chain_create(
                dest=Path(args.path),
                p_wallet=Path(args.wallet),
            )
        elif args.chain_command == 'info':
            ops.chain_info(
                p_chain=Path(args.chain),
                block_limit=args.block_limit,
            )
        elif args.chain_command == 'mine':
            ops.chain_mine(
                p_wallet=Path(args.wallet),
                p_chain=Path(args.chain),
            )
        else:
            chain_parser.print_help()
    elif args.command == 'transaction':
        if args.transaction_command == 'create':
            ops.transaction_create(
                p_wallet=Path(args.wallet),
                p_chain=Path(args.chain),
                receiver=args.receiver,
                amount=args.amount,
            )
        else:
            transaction_parser.print_help()
    else:
        parser.print_help()
