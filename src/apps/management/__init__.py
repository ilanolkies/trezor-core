from trezor.dispatcher import register
from trezor.utils import unimport_func


@unimport_func
def dispatch_LoadDevice(mtype, mbuf):
    from trezor.messages.LoadDevice import LoadDevice

    message = LoadDevice.loads(mbuf)

    from .layout_load_device import layout_load_device
    return layout_load_device(message)


@unimport_func
def dispatch_WipeDevice(mtype, mbuf):
    from trezor.messages.WipeDevice import WipeDevice

    message = WipeDevice.loads(mbuf)

    from .layout_wipe_device import layout_wipe_device
    return layout_wipe_device(message)


def boot():
    LoadDevice = 13
    register(LoadDevice, dispatch_LoadDevice)
    WipeDevice = 5
    register(WipeDevice, dispatch_WipeDevice)