#  _   _      _           _         _      _____   __      __         _ _   
# | \ | |    | |         | |       | |    |  __ \  \ \    / /        | | |  
# |  \| | ___| |__  _   _| | __ _  | |    | |__) |  \ \  / /_ _ _   _| | |_ 
# | . ` |/ _ \ '_ \| | | | |/ _` | | |    |  ___/    \ \/ / _` | | | | | __|
# | |\  |  __/ |_) | |_| | | (_| | | |____| |         \  / (_| | |_| | | |_ 
# |_| \_|\___|_.__/ \__,_|_|\__,_| |______|_|          \/ \__,_|\__,_|_|\__|
#
# Version 2.0

I = importlib

con = Hash(default_value='')

staking = Hash(default_value=0)
locking = Hash(default_value=0)

levels = Variable()

trusted = Variable()
active = Variable()

VALIDATOR = '9a12554c2098567d22aaa9b787d73b606d2f2044a602186c3b9af65f6c58cfaf'

# TODO: Extend
OPERATORS = [
    'ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d'
]

@construct
def seed():
    con['neb'] = 'con_nebula'
    con['key'] = 'con_neb_key001'
    con['dex'] = 'con_rocketswap_official_v1_1'

    # TODO: Set real values for each level
    lvl = list()

    lvl[1]  = {'key':  0, 'neb': decimal(10),  'lp': decimal(1),  'emission': decimal(0.1)}
    lvl[2]  = {'key':  1, 'neb': decimal(20),  'lp': decimal(2),  'emission': decimal(0.5)}
    lvl[3]  = {'key':  2, 'neb': decimal(30),  'lp': decimal(3),  'emission': decimal(1.0)}
    lvl[4]  = {'key':  3, 'neb': decimal(40),  'lp': decimal(4),  'emission': decimal(1.5)}
    lvl[5]  = {'key':  4, 'neb': decimal(50),  'lp': decimal(5),  'emission': decimal(2.0)}
    lvl[6]  = {'key':  5, 'neb': decimal(60),  'lp': decimal(6),  'emission': decimal(2.5)}
    lvl[7]  = {'key':  6, 'neb': decimal(70),  'lp': decimal(7),  'emission': decimal(3.0)}
    lvl[8]  = {'key':  7, 'neb': decimal(80),  'lp': decimal(8),  'emission': decimal(3.5)}
    lvl[9]  = {'key':  8, 'neb': decimal(90),  'lp': decimal(9),  'emission': decimal(4.0)}
    lvl[10] = {'key':  9, 'neb': decimal(100), 'lp': decimal(10), 'emission': decimal(4.5)}
    lvl[11] = {'key': 10, 'neb': decimal(110), 'lp': decimal(11), 'emission': decimal(5.0)}
    lvl[12] = {'key': 11, 'neb': decimal(120), 'lp': decimal(12), 'emission': decimal(5.5)}
    lvl[13] = {'key': 12, 'neb': decimal(130), 'lp': decimal(13), 'emission': decimal(6.0)}
    lvl[14] = {'key': 13, 'neb': decimal(140), 'lp': decimal(14), 'emission': decimal(6.5)}
    lvl[15] = {'key': 14, 'neb': decimal(150), 'lp': decimal(15), 'emission': decimal(7.0)}
    lvl[16] = {'key': 15, 'neb': decimal(160), 'lp': decimal(16), 'emission': decimal(7.5)}
    lvl[17] = {'key': 16, 'neb': decimal(170), 'lp': decimal(17), 'emission': decimal(8.0)}
    lvl[18] = {'key': 17, 'neb': decimal(180), 'lp': decimal(18), 'emission': decimal(8.5)}

    levels.set(lvl)

    trusted.set([])
    active.set(True)

@export
def get_level(address: str):
    key_stake = staking[address, 'key']
    neb_stake = staking[address, 'neb']
    lp_stake = staking[address, 'lp']

    key_level = 0
    neb_level = 0
    lp_level = 0

    lvl = levels.get()

    for i in range(len(lvl), 0, -1):
        level = lvl[i]

        if not lp_level:
            if level['lp'] >= lp_stake:
                lp_level = i

        if not key_level:
            if level['lp'] >= key_stake:
                key_level = i

        if not neb_level:
            if level['lp'] >= neb_stake:
                neb_level = i

    return {'key': key_level, 'neb': neb_level, 'lp': lp_level}

@export
def get_emission(key_level: int, neb_level: int, lp_level: int)
    return levels.get()[key_level + neb_level + lp_level]['emission']

@export
def show_level(address: str):
    return str(get_level(address))

@export
def stake(neb_amount: float = 0, lp_amount: float = 0, key_amount: int = 0):
    assert_active()

    assert isinstance(neb_amount, decimal), 'Type of neb_amount must be float'
    assert isinstance(lp_amount, decimal), 'Type of lp_amount must be float'
    assert isinstance(key_amount, int), 'Type of key_amount must be int'
    assert neb_amount >= 0, 'Negative amounts are not allowed'
    assert lp_amount >= 0, 'Negative amounts are not allowed'
    assert key_amount >= 0, 'Negative amounts are not allowed'

    if neb_amount > 0:
        staking['neb'] += neb_amount
        staking[ctx.caller, 'neb'] += neb_amount

        I.import_module(con['neb']).transfer_from(
            main_account=ctx.caller,
            amount=neb_amount,
            to=ctx.this)

    if lp_amount > 0:
        staking['lp'] += lp_amount
        staking[ctx.caller, 'lp'] += lp_amount

        I.import_module(con['dex']).transfer_liquidity_from(
            contract=con['neb'],
            to=ctx.this, 
            main_account=ctx.caller, 
            amount=lp_amount)   
    
    if key_amount > 0:
        staking['key'] += key_amount
        staking[ctx.caller, 'key'] += key_amount

        I.import_module(con['key']).transfer_from(
            main_account=ctx.caller,
            amount=key_amount,
            to=ctx.this)

@export
def unstake(neb_amount: float = 0, lp_amount: float = 0, key_amount: int = 0):
    assert_active()

    assert isinstance(neb_amount, decimal), 'Type of neb_amount must be float'
    assert isinstance(lp_amount, decimal), 'Type of lp_amount must be float'
    assert isinstance(key_amount, int), 'Type of key_amount must be int'
    assert neb_amount >= 0, 'Negative amounts are not allowed'
    assert lp_amount >= 0, 'Negative amounts are not allowed'
    assert key_amount >= 0, 'Negative amounts are not allowed'

    staked_lp = staking[ctx.caller, 'lp']
    staked_neb = staking[ctx.caller, 'neb']
    staked_key = staking[ctx.caller, 'key']

    highest_lp = 0
    highest_neb = 0
    highest_key = 0

    if isinstance(locking[ctx.caller], list):
        for lock_contract in locking[ctx.caller]:
            locked_lp = locking[ctx.caller, lock_contract, 'lp']
            locked_neb = locking[ctx.caller, lock_contract, 'neb']
            locked_key = locking[ctx.caller, lock_contract, 'key']

            if locked_lp > highest_lp: highest_lp = locked_lp
            if locked_neb > highest_neb: highest_neb = locked_neb
            if locked_key > highest_key: highest_key = locked_key

    lp_available = staked_lp - highest_lp
    neb_available = staked_neb - highest_neb
    key_available = staked_key - highest_key

    assert lp_available >= lp_amount, f'Only {lp_available} NEB LP available to unstake'
    assert neb_available >= neb_amount, f'Only {neb_available} NEB available to unstake'
    assert key_available >= key_amount, f'Only {key_available} NEB KEY available to unstake'

    if lp_amount > 0:
        I.import_module(con['dex']).transfer_liquidity(
            contract=con['neb'],
            to=ctx.caller, 
            amount=lp_amount)

    if neb_amount > 0:
        I.import_module(con['neb']).transfer(
            amount=neb_amount,
            to=ctx.caller)

    if key_amount > 0:
        I.import_module(con['key']).transfer(
            amount=key_amount,
            to=ctx.caller)

    staking[ctx.caller, 'lp'] -= lp_amount
    staking[ctx.caller, 'neb'] -= neb_amount
    staking[ctx.caller, 'key'] -= key_amount

    staking['lp'] -= lp_amount
    staking['neb'] -= neb_amount
    staking['key'] -= key_amount

@export
def lock():
    user_address = ctx.signer
    vault_contract = ctx.caller

    assert vault_contract in trusted.get(), f'Unknown contract {vault_contract}'
    assert vault_contract.startswith('con_'), 'Caller needs to be a contract'

    if not isinstance(locking[user_address], list):
        locking[user_address] = []

    lock_list = locking[user_address]

    if not vault_contract in lock_list:
        lock_list.append(vault_contract)

    locking[user_address] = lock_list

    locking[user_address, vault_contract, 'key'] = staking[user_address, 'key']
    locking[user_address, vault_contract, 'neb'] = staking[user_address, 'neb']
    locking[user_address, vault_contract, 'lp'] = staking[user_address, 'lp']

    lvl = get_level(user_address)
    return get_emission(lvl['key'], lvl['neb'], lvl['lp'])

@export
def unlock():
    user_address = ctx.signer
    vault_contract = ctx.caller

    assert vault_contract in trusted.get(), f'Unknown contract {vault_contract}'
    assert vault_contract.startswith('con_'), 'Caller needs to be a contract'

    lock_list = locking[user_address]
    
    if vault_contract in lock_list:
        lock_list.remove(vault_contract)
    
    locking[user_address] = lock_list

    locking[user_address, vault_contract, 'key'] = int(0)
    locking[user_address, vault_contract, 'neb'] = decimal(0)
    locking[user_address, vault_contract, 'lp'] = decimal(0)

@export
def set_contract(key: str, value: str):
    assert_caller_is_owner()
    con[key] = value

@export
def adjust_level(level: int, data: dict):
    assert_caller_is_owner()
    lvl = levels.get()
    lvl[level] = data

@export
def add_valid_vault(contract_name: str):
    assert_caller_is_validator()
    
    trusted_contracts = trusted.get()
    if contract_name not in trusted_contracts:
        trusted_contracts.append(contract_name)
        trusted.set(trusted_contracts)

@export
def remove_valid_vault(contract_name: str):
    assert_caller_is_validator()
    
    trusted_contracts = trusted.get()
    if contract_name in trusted_contracts:
        trusted_contracts.remove(contract_name)
        trusted.set(trusted_contracts)

@export
def emergency_lock(user_address: str, vault_contract: str, lp_amount: float, neb_amount: float, key_amount: int):
    assert_caller_is_owner()

    assert isinstance(key_amount, int), 'Type of key_amount must be int'
    assert isinstance(neb_amount, decimal), 'Type of neb_amount must be float'
    assert isinstance(lp_amount, decimal), 'Type of lp_amount must be float'

    if not isinstance(locking[user_address], list):
        locking[user_address] = []

    lock_list = locking[user_address]

    if not vault_contract in lock_list:
        lock_list.append(vault_contract)

    locking[user_address] = lock_list

    locking[user_address, vault_contract, 'key'] = key_amount
    locking[user_address, vault_contract, 'neb'] = neb_amount
    locking[user_address, vault_contract, 'lp'] = lp_amount

@export
def emergency_unlock(user_address: str, vault_contract: str):
    assert_caller_is_owner()

    lock_list = locking[user_address]
    
    if vault_contract in lock_list:
        lock_list.remove(vault_contract)
    
    locking[user_address] = lock_list

    locking[user_address, vault_contract, 'key'] = int(0)
    locking[user_address, vault_contract, 'neb'] = decimal(0)
    locking[user_address, vault_contract, 'lp'] = decimal(0)

@export
def emergency_withdraw_token(contract_name: str, amount: float):
    I.import_module(contract_name).transfer(amount, ctx.caller)
    assert_caller_is_owner()

@export
def emergency_withdraw_lp(contract_name: str, amount: float):
    I.import_module(con['dex']).transfer_liquidity(contract_name, ctx.caller, amount)
    assert_caller_is_owner()

@export
def active(is_active: bool):
    assert_caller_is_owner()
    active.set(is_active)

def assert_active():
    assert active.get() == True, 'Vault inactive!'

def assert_caller_is_owner():
    assert ctx.caller in OPERATORS, 'Only executable by operators!'

def assert_caller_is_validator():
    assert ctx.caller == VALIDATOR, 'Only executable by validator!'
