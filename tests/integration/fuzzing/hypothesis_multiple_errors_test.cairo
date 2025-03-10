%lang starknet

from starkware.cairo.common.math import assert_nn

@external
func test_hypothesis_multiple_errors{syscall_ptr : felt*, range_check_ptr}(x : felt):
    with_attr error_message("Must be positive."):
        assert_nn(x)
    end

    %{ expect_revert("Cannot withdraw more than stored.") %}
    with_attr error_message("Cannot withdraw more than stored."):
        assert_nn(1000 - x)
    end

    return ()
end
