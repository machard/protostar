%lang starknet

from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write
from starkware.cairo.common.uint256 import Uint256

@view
func assert_pranked{syscall_ptr : felt*}():
    let (caller_addr) = get_caller_address()
    with_attr error_message("Not pranked"):
        assert caller_addr = 123
    end
    return ()
end
