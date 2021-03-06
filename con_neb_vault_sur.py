#  _   _      _           _          _____                  _                  __      __         _ _   
# | \ | |    | |         | |        / ____|                (_)                 \ \    / /        | | |  
# |  \| | ___| |__  _   _| | __ _  | (___  _   _ _ ____   _____   _____  _ __   \ \  / /_ _ _   _| | |_ 
# | . ` |/ _ \ '_ \| | | | |/ _` |  \___ \| | | | '__\ \ / / \ \ / / _ \| '__|   \ \/ / _` | | | | | __|
# | |\  |  __/ |_) | |_| | | (_| |  ____) | |_| | |   \ V /| |\ V / (_) | |       \  / (_| | |_| | | |_ 
# |_| \_|\___|_.__/ \__,_|_|\__,_| |_____/ \__,_|_|    \_/ |_| \_/ \___/|_|        \/ \__,_|\__,_|_|\__|
#
# Version 1.2

I = importlib

staking = Hash(default_value=0.0)
payouts = Hash(default_value=0.0)

start_date = Variable()
lock_date = Variable()
end_date = Variable()

total_stake = Variable()
total_emission = Variable()

funding_contract = Variable()
funding_amount = Variable()

stake_contract = Variable()
unstake_tax = Variable()
active = Variable()

OPERATORS = [
    'ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d',
    'e787ed5907742fa8d50b3ca2701ab8e03ec749ced806a15cdab800a127d7f863',
    '62783e94c14b0ae0c555f33ca6aa9699099606d636d4f0fd916bf912d8022045'
]

@export
def init(minutes_to_start: int, minutes_to_lock: int, minutes_to_end: int, stake_token_contract: str, 
         pre_funding_token_contract: str = '', pre_funding_token_amount: float = 0, early_unstake_tax: float = 5):

    assert isinstance(pre_funding_token_amount, decimal), 'Type of pre_funding_token_amount must be float'
    assert isinstance(early_unstake_tax, decimal), 'Type of early_unstake_tax must be float'
    assert isinstance(minutes_to_start, int), 'Type of minutes_to_start must be int'
    assert isinstance(minutes_to_lock, int), 'Type of minutes_to_lock must be int'
    assert isinstance(minutes_to_end, int), 'Type of minutes_to_end must be int'

    sc = I.import_module(stake_token_contract)

    if pre_funding_token_contract:
        assert pre_funding_token_amount > 0, 'Pre-funding token amount must be > 0'
        fc = I.import_module(pre_funding_token_contract)
    if pre_funding_token_amount:
        assert pre_funding_token_amount > 0, 'Pre-funding token amount must be > 0'
        assert pre_funding_token_contract, 'Pre-funding token contract must be set'

    if stake_token_contract.lower() in ['currency', 'con_nebula']:
        assert_owner('This staking token can only be used by the Nebula team')

    total_stake.set(decimal(0))
    total_emission.set(decimal(0))

    funding_contract.set(pre_funding_token_contract)
    funding_amount.set(pre_funding_token_amount)

    stake_contract.set(stake_token_contract)
    unstake_tax.set(early_unstake_tax)

    start_date.set(now + datetime.timedelta(minutes=minutes_to_start))
    lock_date.set(start_date.get() + datetime.timedelta(minutes=minutes_to_lock))
    end_date.set(lock_date.get() + datetime.timedelta(minutes=minutes_to_end))

    if funding_contract.get() and funding_amount.get():
        I.import_module(funding_contract.get()).transfer_from(
            amount=funding_amount.get(),
            main_account=ctx.caller,
            to=ctx.this)

    active.set(True)

@export
def active(is_active: bool):
    active.set(is_active)
    assert_owner()

@export
def stake(amount: float):
    assert_active()

    assert amount > 0, 'Negative amounts are not allowed'
    assert isinstance(amount, decimal), 'Type of amount must be float'
    assert now > start_date.get(), f'Staking not started yet: {start_date.get()}'
    assert now < lock_date.get(), f'Staking already ended: {lock_date.get()}'

    I.import_module(stake_contract.get()).transfer_from(
        main_account=ctx.caller,
        amount=amount,
        to=ctx.this)

    staking[ctx.caller] += amount
    total_stake.set(total_stake.get() + amount)

@export
def unstake():
    assert_active()

    assert staking[ctx.caller] > 0, f'No stake found for this address'

    # You survived! Pay out stake + emissions (+ pre funding if set)
    if now > end_date.get():
        stake_percent = staking[ctx.caller] / total_stake.get() * 100
        stake_emission = total_emission.get() / 100 * stake_percent

        payouts[ctx.caller, stake_contract.get()] = staking[ctx.caller] + stake_emission

        I.import_module(stake_contract.get()).transfer(
            amount=payouts[ctx.caller, stake_contract.get()],
            to=ctx.caller)

        if funding_amount.get():
            funding_emission = funding_amount.get() / 100 * stake_percent

            payouts[ctx.caller, funding_contract.get()] += funding_emission

            I.import_module(funding_contract.get()).transfer(
                amount=funding_emission,
                to=ctx.caller)

    # No diamond hands? Pay out stake - early unstake tax
    else:
        tax = staking[ctx.caller] / 100 * unstake_tax.get()
        total_emission.set(total_emission.get() + tax)

        payouts[ctx.caller, stake_contract.get()] = staking[ctx.caller] - tax
        total_stake.set(total_stake.get() - staking[ctx.caller])

        I.import_module(stake_contract.get()).transfer(
            amount=payouts[ctx.caller, stake_contract.get()],
            to=ctx.caller)

    staking[ctx.caller] = decimal(0)

    stake_payout = payouts[ctx.caller, stake_contract.get()]
    funding_payout = payouts[ctx.caller, funding_contract.get()]

    return f'{funding_contract.get()}: {funding_payout}, {stake_contract.get()}: {stake_payout}'

@export
def emergency_withdraw(contract: str, amount: float):
    I.import_module(contract).transfer(amount, ctx.caller)
    assert_owner()

@export
def emergency_set_stake(address: str, amount: float):
    staking[address] = amount
    assert_owner()

def assert_active():
    assert active.get() == True, 'Vault inactive!'

def assert_owner(msg: str = ''):
    error_msg = msg if msg else 'Only executable by operators!'
    assert ctx.caller in OPERATORS, error_msg
