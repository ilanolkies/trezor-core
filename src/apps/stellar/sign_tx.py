from apps.common import seed
from apps.stellar.writers import *
from apps.stellar.operations import operation
from apps.stellar import layout
from apps.stellar import consts
from apps.stellar import helpers
from trezor.messages.StellarSignTx import StellarSignTx
from trezor.messages.StellarTxOpRequest import StellarTxOpRequest
from trezor.messages.StellarSignedTx import StellarSignedTx
from trezor.crypto.curve import ed25519
from trezor.crypto.hashlib import sha256
from trezor.loop import spawn, sleep, wait
from ubinascii import hexlify

STELLAR_CURVE = 'ed25519'
TX_TYPE = bytearray('\x00\x00\x00\x02')


async def sign_tx_loop(ctx, msg: StellarSignTx):
    signer = sign_tx(ctx, msg)
    res = None
    while True:
        req = signer.send(res)
        if isinstance(req, StellarTxOpRequest):
            res = await ctx.call(req, *consts.op_wire_types)
        elif isinstance(req, StellarSignedTx):
            break
        elif isinstance(req, helpers.UiConfirmInit):
            res = await layout.require_confirm_init(ctx, req.pubkey, req.network)
        elif isinstance(req, helpers.UiConfirmMemo):
            res = await layout.require_confirm_memo(ctx, req.memo_type, req.memo_text)
        elif isinstance(req, helpers.UiConfirmFinal):
            res = await layout.require_confirm_final(ctx, req.fee, req.num_operations)
        elif isinstance(req, (spawn, sleep, wait)):
            res = await req
            continue
        else:
            raise TypeError('Stellar: Invalid signing instruction')
    return req


async def sign_tx(ctx, msg):
    if msg.num_operations == 0:
        raise ValueError('Stellar: At least one operation is required')

    network_passphrase_hash = sha256(msg.network_passphrase).digest()

    # Stellar transactions consist of sha256 of:
    # - sha256(network passphrase)
    # - 4-byte unsigned big-endian int type constant (2 for tx)
    # - public key

    w = bytearray()
    write_bytes(w, network_passphrase_hash)
    write_bytes(w, TX_TYPE)

    node = await seed.derive_node(ctx, msg.address_n, STELLAR_CURVE)
    pubkey = seed.remove_ed25519_public_key_prefix(node.public_key())
    write_pubkey(w, pubkey)
    if msg.source_account != pubkey:
        raise ValueError('Stellar: source account does not match address_n')

    # confirm init
    await helpers.confirm_init(pubkey, msg.network_passphrase)

    write_uint32(w, msg.fee)
    write_uint64(w, msg.sequence_number)

    # timebounds are only present if timebounds_start or timebounds_end is non-zero
    if msg.timebounds_start or msg.timebounds_end:
        write_bool(w, True)
        # timebounds are sent as uint32s since that's all we can display, but they must be hashed as 64bit
        write_uint64(w, msg.timebounds_start)
        write_uint64(w, msg.timebounds_end)
    else:
        write_bool(w, False)

    write_uint32(w, msg.memo_type)
    if msg.memo_type == consts.MEMO_TYPE_NONE:
        # nothing is serialized
        memo_confirm_text = ''
    elif msg.memo_type == consts.MEMO_TYPE_TEXT:
        # Text: 4 bytes (size) + up to 28 bytes
        if len(msg.memo_text) > 28:
            raise ValueError('Stellar: max length of a memo text is 28 bytes')
        write_string(w, msg.memo_text)
        memo_confirm_text = msg.memo_text
    elif msg.memo_type == consts.MEMO_TYPE_ID:
        # ID: 64 bit unsigned integer
        write_uint64(w, msg.memo_id)
        memo_confirm_text = str(msg.memo_id)
    elif msg.memo_type in [consts.MEMO_TYPE_HASH, consts.MEMO_TYPE_RETURN]:
        # Hash/Return: 32 byte hash
        write_bytes(w, bytearray(msg.memo_hash))
        memo_confirm_text = hexlify(msg.memo_hash).decode()
    else:
        raise ValueError('Stellar invalid memo type')
    await helpers.confirm_memo(msg.memo_type, memo_confirm_text)

    write_uint32(w, msg.num_operations)
    for i in range(msg.num_operations):
        op = yield StellarTxOpRequest()
        await operation(ctx, w, op)

    # 4 null bytes representing a (currently unused) empty union
    write_uint32(w, 0)

    # confirms
    await helpers.confirm_final(msg.fee, msg.num_operations)

    # sign
    # (note that the signature does not include the 4-byte hint since it can be calculated from the public key)
    digest = sha256(w).digest()
    signature = ed25519.sign(node.private_key(), digest)

    # Add the public key for verification that the right account was used for signing
    resp = StellarSignedTx()
    resp.public_key = pubkey
    resp.signature = signature

    yield resp


def node_derive(root, address_n: list):
    node = root.clone()
    node.derive_path(address_n)
    return node
