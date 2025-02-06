MAX_RETRIES = 2

SECURITY_UNIQUE_FIELD = [
    'id'
]

DEPOSIT_UNIQUE_FIELD = [
    'id'
]

DEPOSIT_UPDATE_FIELDS = [
    'bank_account_id',
    'status',
    'currency',
    'amount',
    'cancelled_at',
    'rejected_at',
    'accepted_at',
    'created_at',
    'last_synced',
    'account_id'
]

QUESTRADE_ACTIVITY_TYPE_DICT = {
    "FX conversion" : "Convert Funds",
    "Dividends" : "Dividend",
    "Trades" : "Order",
    "Deposits" : "Deposit",
    "Corporate actions" : "Corporate Action",
    "Order": "Order",
    "Fees and rebates": "Fees and Rebates",
    "Option": "Option",
    "Other" : "Other"

}

WSIMPLE_ACTIVITY_TYPE_DICT = {
    "institutional_transfer" : "Institutional Transfer",
    "order" : "Order",
    "convert_funds" : "Convert Funds",
    "dividend" : "Dividend",
    "internal_transfer": "Internal Transfer",
    "fpl_securities_lending": "Securities Lending",
    "fpl_interest_earnings": "Interest Earnings"
}

SECURITYGROUP_UNIQUE_FIELD = [
    'id'
]

ACCOUNT_UNIQUE_FIELD = [
    'account_number'
]

ACTIVITY_UNIQUE_FIELD = [
    'id'
]

ACCOUNTPOSITION_UNIQUE_FIELD = [
    'security_id',
    'account_id'
]

SECURITY_UPDATE_FIELDS = [
    'name',
    'description',
    'type',
    'currency',
    'status',
    'exchange',
    'option_details',
    'order_subtypes',
    'trade_eligible',
    'options_eligible',
    'buyable',
    'sellable',
    'active_date',
    'last_synced'
]

ACCOUNT_UPDATE_FIELDS = [
    'type',
    'current_balance',
    'net_deposits',
    'currency',
    'status',
    'updated_at',
    'last_synced'
]

ACTIVITY_UPDATE_FIELDS = [
    'currency',
    'type',
    'sub_type',
    'action',
    'stop_price',
    'price',
    'quantity',
    'amount',
    'commission',
    'option_multiplier',
    'security_id',
    'symbol',
    'market_currency',
    'status',
    'cancelled_at',
    'rejected_at',
    'submitted_at',
    'filled_at',
    'created_at',
    'last_updated',
    'last_synced',
    'security_id'
]

SECURITYGROUP_UPDATE_FIELDS = [
    'name',
    'description'
]

ACCOUNTPOSITION_UPDATE_FIELDS = [
    'quantity',
    'amount',
    'is_active',
    'security_id',
    'account_id'
]

WEALTHSIMPLE_ACITIVITIES_TYPES = [
        "all",
        "deposit",
        "withdrawal",
        "buy",
        "sell",
        "dividend",
        "institutional_transfer",
        "internal_transfer",
        "refund",
        "referral_bonus",
        "affiliate",
    ]