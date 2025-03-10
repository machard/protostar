# `deploy_contract`

```python
def deploy_contract(
    self,
    contract_path: str,
    constructor_args: Optional[List[int]] = None,
    *,
    config: Optional[CheatcodeNetworkConfig] = None
) -> DeployedContract: ...

@dataclass(frozen=True)
class DeployedContract:
    contract_address: int
```


Deploys a **compiled** contract given a path relative to the project root.

`config` is a keyword only argument that allows passing [network configuration](../03-network-config.md) data. See related documentation for more information.

:::warning
Don't use `starkware.starknet.common.syscalls.deploy`. It will deploy the contract to the Protostar's local StarkNet.
:::




## Example

```cairo
%lang starknet

@external
func up():
    %{ deploy_contract("./build/main.json", config={"wait_for_acceptance": True}) %}

    return ()
end
```