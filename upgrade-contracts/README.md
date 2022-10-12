# Upgradable Smart Contracts
An implementation of upgrading smart contracts using the *transparent proxy pattern* as seen by OpenZeppelin. These smart contracts also implement a **ProxyAdmin** contract as the main admin control source for all future proxy contracts. The Deploy script upgrades an implementation contract two times (for a total of 3 unique `Box` contracts).

## Diagram of Implementation

```
User ---- tx ---> Proxy ----------> Box.sol
                    |
                    --------------> BoxV2.sol
                    |
                    --------------> BoxV3.sol
```