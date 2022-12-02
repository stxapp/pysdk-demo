# Quick Start

The SDK is composed of two key sections:

 - **Proxy** (the classes providing the low-level functionality)
 - **Client** (the services to be used for connectivity with the STX APIs).

All you need to use is **Client** services for the integration with the APIs.

There are two services available **StxClient** and **StxChannelClient**

 - **StxClient** provides sync operations, while
 - **StxChannelClient** provides connectivity with websocket channels.

### StxClient

It provides the following operations:

1. login
2. confirm2Fa
3. send2Fa
4. logout
5. updateProfile
6. updateUserProfile
7. confirmOrder
8. cancelOrder
9. cancelOrders
10. cancelAllOrders
11. userProfile
12. marketFilterTree
13. marketInfos
14. marketSettlements
15. accountMarketStats
16. accountLimitsNumber
17. accountLimitsHistoryNumber
18. myDepositAndWithdrawalHistory
19. myOrderHistory
20. mySettlementsHistory
21. myTradesForOrder
22. myTradesHistory
23. tradesForSettlement

### StxChannelClient
It provides the following websocket APIs:

1. portfolio_join
2. market_info_join
3. active_trades_join
4. active_orders_join
5. active_settlements_join
6. active_positions_join
