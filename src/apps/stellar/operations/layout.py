from apps.stellar.layout import *
from trezor.messages import ButtonRequestType
from trezor.ui.text import Text

from trezor.messages.StellarAccountMergeOp import StellarAccountMergeOp
from trezor.messages.StellarAssetType import StellarAssetType
from trezor.messages.StellarAllowTrustOp import StellarAllowTrustOp
from trezor.messages.StellarBumpSequenceOp import StellarBumpSequenceOp
from trezor.messages.StellarChangeTrustOp import StellarChangeTrustOp
from trezor.messages.StellarCreateAccountOp import StellarCreateAccountOp
from trezor.messages.StellarCreatePassiveOfferOp import StellarCreatePassiveOfferOp
from trezor.messages.StellarManageDataOp import StellarManageDataOp
from trezor.messages.StellarManageOfferOp import StellarManageOfferOp
from trezor.messages.StellarPathPaymentOp import StellarPathPaymentOp
from trezor.messages.StellarPaymentOp import StellarPaymentOp
from trezor.messages.StellarSetOptionsOp import StellarSetOptionsOp
from utime import sleep


# todo done
async def confirm_source_account(ctx, source_account: bytes):
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.BOLD, 'Source account:',
                   ui.MONO, *split(format_address(source_account)),
                   icon_color=ui.GREEN)
    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)
    # sleep(5)


# todo done
async def confirm_allow_trust_op(ctx, op: StellarAllowTrustOp):
    if op.is_authorized:
        text = 'Allow'
    else:
        text = 'Revoke'
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.BOLD, text + ' Trust',
                   ui.NORMAL, "of '" + op.asset_code + "' by:",
                   ui.MONO, *split(trim_to_rows(format_address(op.trusted_account), 3)),
                   icon_color=ui.GREEN)

    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)
    # sleep(10)


# todo done
async def confirm_account_merge_op(ctx, op: StellarAccountMergeOp):
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.BOLD, 'Account Merge',
                   ui.NORMAL, 'All XLM will be sent to:',
                   ui.MONO, *split(trim_to_rows(format_address(op.destination_account), 3)),
                   icon_color=ui.GREEN)
    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)
    sleep(5)


# todo done
async def confirm_bump_sequence_op(ctx, op: StellarBumpSequenceOp):
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.BOLD, 'Bump Sequence',
                   ui.NORMAL, 'Set sequence to',
                   ui.MONO, str(op.bump_to),
                   icon_color=ui.GREEN)
    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)
    # sleep(5)


# todo done
async def confirm_change_trust_op(ctx, op: StellarChangeTrustOp):
    if op.limit == 0:
        text = 'Delete'
    else:
        text = 'Add'
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.BOLD, text + ' Trust',
                   ui.NORMAL, 'asset: ' + op.asset.code,
                   ui.NORMAL, 'amount: ' + format_amount(op.limit),
                   ui.MONO, *split(trim_to_rows(format_address(op.asset.issuer), 2)),
                   icon_color=ui.GREEN)
    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)
    # sleep(10)


# todo done
async def confirm_create_account_op(ctx, op: StellarCreateAccountOp):
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.BOLD, 'Create Account',
                   ui.NORMAL, 'with ' + format_amount(op.starting_balance),
                   ui.MONO, *split(trim_to_rows(format_address(op.new_account), 3)),
                   icon_color=ui.GREEN)
    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)


# todo scale ?? asset issuer too long
async def confirm_create_passive_offer_op(ctx, op: StellarCreatePassiveOfferOp):
    if op.amount == 0:
        text = 'Delete'
    else:
        text = 'New'
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.BOLD, text + ' Passive Offer',
                   ui.NORMAL, 'Sell ' + str(op.amount) + ' ' + op.selling_asset.code,
                   ui.NORMAL, 'For ' + str(op.price_n / op.price_d) + ' per',
                   ui.NORMAL, format_asset_type(op.buying_asset),
                   icon_color=ui.GREEN)
    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)
    sleep(10)


# todo display op.value?
async def confirm_manage_data_op(ctx, op: StellarManageDataOp):
    if op.value:
        text = 'Set'
    else:
        text = 'Clear'
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.BOLD, text + ' data value key',
                   ui.MONO, *split(op.key),
                   icon_color=ui.GREEN)
    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)
    # if op.value:
    # sleep(10)


# todo
# async def confirm_manage_offer_op(ctx, op: StellarManageOfferOp):
    # todo

# todo done
async def confirm_path_payment_op(ctx, op: StellarPathPaymentOp):
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.BOLD, 'Path Pay ' + format_amount(op.destination_amount, ticker=False),
                   ui.BOLD, format_asset_type(op.destination_asset) + ' to:',
                   ui.MONO, *split(trim_to_rows(format_address(op.destination_account), 3)),
                   icon_color=ui.GREEN)
    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)
    # sleep(5)

    # confirm what the sender is using to pay
    content = Text('Confirm operation', ui.ICON_CONFIRM,
                   ui.NORMAL, 'Pay using',
                   ui.BOLD, format_amount(op.send_max),
                   ui.BOLD, format_asset_type(op.send_asset),
                   ui.NORMAL, 'This amount is debited',
                   ui.NORMAL, 'from your account.',
                   icon_color=ui.GREEN)
    await require_confirm(ctx, content, ButtonRequestType.ConfirmOutput)
    # sleep(5)


def format_asset_type(asset: StellarAssetType) -> str:
    """
    Returns the asset formatted to fit in a single row
    Examples:
        XLM (native asset)
        MOBI (G1234)
        ALPHA12EXAMP (G0987)
    """
    if asset.type == consts.ASSET_TYPE_NATIVE:
        return 'XLM (native asset)'

    # get string representation of address
    issuer = format_address(asset.issuer)
    if asset.type in [consts.ASSET_TYPE_ALPHANUM4, consts.ASSET_TYPE_ALPHANUM12]:
        issuer = trim(issuer, 7, dots=False)
        return asset.code + ' (' + issuer + ')'  # todo security - ok to short?
